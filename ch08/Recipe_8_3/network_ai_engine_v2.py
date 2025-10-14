import json

class EnhancedNetworkCopilot:
    def __init__(self, model_name="gpt-4o-mini"):
        self.conversation = []
        self.current_device = None
        self.model_name = model_name
        self.load_all_data()
    
    def load_all_data(self):
        """Load all network knowledge data from files"""
        with open('mock_data/devices.json') as f:
            self.devices = json.load(f)
        with open('mock_data/network_context.json') as f:
            self.network_context = json.load(f)
        with open('mock_data/topology.json') as f:
            self.topology = json.load(f)
        with open('mock_data/templates.json') as f:
            self.templates = json.load(f)
    
    def get_device_relationships(self, device_name):
        """Get connected devices and interface mappings"""
        if device_name not in self.topology['connections']:
            return {}
        
        relationships = {}
        connections = self.topology['connections'][device_name]
        
        for local_interface, connection_info in connections.items():
            remote_device = connection_info['connects_to']
            remote_interface = connection_info['interface']
            
            relationships[remote_device] = {
                'local_interface': local_interface,
                'remote_interface': remote_interface,
                'connection_type': connection_info.get('vlan', connection_info.get('subnet', 'unknown'))
            }
        
        return relationships
    
    def find_affected_devices(self, device_name):
        """Find devices that might be affected by changes"""
        affected = set()
        
        # Direct connections
        relationships = self.get_device_relationships(device_name)
        affected.update(relationships.keys())
        
        # Check service dependencies
        for service, dependent_devices in self.topology['dependencies'].items():
            if device_name in dependent_devices:
                affected.update(dependent_devices)
        
        affected.discard(device_name)  # Remove self
        return list(affected)
    
    def get_configuration_template(self, config_type, device_type):
        """Get appropriate configuration template"""
        templates = self.templates['configurations']
        
        for template_name, template_info in templates.items():
            if (config_type in template_name and 
                device_type in template_info.get('device_types', [])):
                return template_info
        
        return None
    
    def analyze_network_impact(self, device_name, proposed_change):
        """Analyze potential impact of network changes"""
        analysis = {
            'affected_devices': self.find_affected_devices(device_name),
            'services_impacted': [],
            'recommendations': []
        }
        
        # Check service dependencies
        for service, devices in self.topology['dependencies'].items():
            if device_name in devices:
                analysis['services_impacted'].append(service)
        
        # Add recommendations based on impact
        if analysis['affected_devices']:
            analysis['recommendations'].append(
                f"Changes to {device_name} may affect: {', '.join(analysis['affected_devices'])}"
            )
        
        if analysis['services_impacted']:
            analysis['recommendations'].append(
                f"Services that may be impacted: {', '.join(analysis['services_impacted'])}"
            )
        
        return analysis
    
    def build_enhanced_context(self, message, intent):
        """Build comprehensive context including relationships and templates"""
        context_parts = []
        
        # Get basic device context
        device_context = self.get_device_context(message)
        if device_context != "Standard network":
            context_parts.append(device_context)
        
        # Add relationship information
        if self.current_device:
            relationships = self.get_device_relationships(self.current_device)
            if relationships:
                connections = []
                for remote_device, conn_info in relationships.items():
                    connections.append(f"{remote_device} via {conn_info['local_interface']}")
                context_parts.append(f"Connected to: {', '.join(connections)}")
        
        # Add relevant templates
        if intent == "configuration" and self.current_device:
            device_type = self.devices[self.current_device]['type']
            msg_lower = message.lower()
            
            config_types = ['ospf', 'vlan', 'trunk', 'access', 'bgp']
            for config_type in config_types:
                if config_type in msg_lower:
                    template = self.get_configuration_template(config_type, device_type)
                    if template:
                        context_parts.append(f"Template available: {template['template']}")
                        context_parts.append(f"Required variables: {', '.join(template['variables'])}")
                    break
        
        # Add standards and best practices
        standards = self.templates.get('standards', {})
        if 'security' in message.lower():
            security_features = standards.get('security', {}).get('required_features', [])
            if security_features:
                context_parts.append(f"Security requirements: {', '.join(security_features)}")
        
        return " | ".join(context_parts) if context_parts else "Standard network"
    
    def get_device_context(self, message):
        """Enhanced device context detection"""
        msg = message.lower()
        context_parts = []
        
        for device_name, device_info in self.devices.items():
            if device_name.lower() in msg:
                self.current_device = device_name
                context_parts.append(f"Device: {device_name}")
                context_parts.append(f"Type: {device_info['type']} ({device_info['model']})")
                context_parts.append(f"Location: {device_info['location']}")
                context_parts.append(f"Protocols: {', '.join(device_info['protocols'])}")
                break
        
        return " | ".join(context_parts) if context_parts else "Standard network"
    
    def get_intent(self, message):
        """Intent detection"""
        msg = message.lower()
        if "configure" in msg or "create" in msg or "setup" in msg:
            return "configuration"
        elif "problem" in msg or "troubleshoot" in msg or "down" in msg or "not working" in msg:
            return "troubleshooting" 
        elif "explain" in msg or "what is" in msg or "how does" in msg:
            return "explanation"
        return "general"
    
    def call_openai_with_knowledge(self, message, intent, enhanced_context):
        """Call OpenAI with enhanced network knowledge"""
        import openai
        client = openai.OpenAI()
        
        # Analyze potential impact
        impact_analysis = {}
        if self.current_device and intent == "configuration":
            impact_analysis = self.analyze_network_impact(self.current_device, message)
        
        system_prompt = """You are an expert network engineering assistant with deep knowledge of 
        network topologies, device relationships, and configuration standards. Always consider the 
        impact of changes on connected devices and dependent services. Use provided templates and 
        follow security best practices. Provide specific, actionable guidance."""
        
        user_prompt = f"""Enhanced Network Context: {enhanced_context}

User Intent: {intent}
User Message: {message}"""

        if impact_analysis and impact_analysis['affected_devices']:
            user_prompt += f"""

Impact Analysis:
- Affected devices: {', '.join(impact_analysis['affected_devices'])}
- Services impacted: {', '.join(impact_analysis['services_impacted'])}
- Recommendations: {'; '.join(impact_analysis['recommendations'])}"""

        user_prompt += "\n\nProvide specific networking guidance considering device relationships, templates, and potential impacts."

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        return response.choices[0].message.content
    
    def chat(self, message):
        """Enhanced chat with network knowledge integration"""
        intent = self.get_intent(message)
        enhanced_context = self.build_enhanced_context(message, intent)
        
        response = self.call_openai_with_knowledge(message, intent, enhanced_context)
        
        # Store conversation with enhanced metadata
        self.conversation.append({
            "user": message,
            "response": response,
            "device": self.current_device,
            "intent": intent,
            "relationships": self.get_device_relationships(self.current_device) if self.current_device else {}
        })
        
        return response

# Interactive mode with enhanced knowledge
if __name__ == "__main__":
    print("Enhanced Network Co-Pilot with Knowledge Integration")
    print("Type 'quit' to exit, 'topology' to see connections")
    print("=" * 55)
    
    try:
        copilot = EnhancedNetworkCopilot()
        
        print("\nAvailable devices:", ", ".join(copilot.devices.keys()))
        print("Try: 'Configure OSPF on R1' or 'What happens if SW1 goes down?'\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'topology':
                print("\nNetwork Connections:")
                for device, connections in copilot.topology['connections'].items():
                    print(f"  {device}:")
                    for interface, conn in connections.items():
                        print(f"    {interface} -> {conn['connects_to']} ({conn['interface']})")
                print()
                continue
            
            if not user_input:
                continue
                
            try:
                response = copilot.chat(user_input)
                print(f"\nCo-Pilot: {response}")
                
                if copilot.current_device:
                    relationships = copilot.get_device_relationships(copilot.current_device)
                    if relationships:
                        connected = list(relationships.keys())
                        print(f"\n[{copilot.current_device} is connected to: {', '.join(connected)}]")
                
                print()
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"\nSession ended. Total conversations: {len(copilot.conversation)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please create all required mock_data files")
    except Exception as e:
        print(f"Setup error: {e}")
        print("Make sure to set OPENAI_API_KEY environment variable")