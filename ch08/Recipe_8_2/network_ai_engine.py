import json

class NetworkCopilot:
    def __init__(self, model_name="gpt-4o-mini"):
        self.conversation = []
        self.current_device = None
        self.model_name = model_name
        self.load_data()
    
    def load_data(self):
        """Load all mock data files"""
        with open('mock_data/devices.json') as f:
            self.devices = json.load(f)
        with open('mock_data/network_context.json') as f:
            self.network_context = json.load(f)
        with open('mock_data/ai_examples.json') as f:
            self.ai_examples = json.load(f)
    
    def get_intent(self, message):
        """Simple intent detection"""
        msg = message.lower()
        if "configure" in msg or "create" in msg or "setup" in msg:
            return "configuration"
        elif "problem" in msg or "troubleshoot" in msg or "down" in msg or "not working" in msg:
            return "troubleshooting" 
        elif "explain" in msg or "what is" in msg or "how does" in msg:
            return "explanation"
        return "general"
    
    def get_device_context(self, message):
        """Get detailed device context"""
        msg = message.lower()
        context_parts = []
        
        # Find mentioned device
        for device_name, device_info in self.devices.items():
            if device_name.lower() in msg:
                self.current_device = device_name
                context_parts.append(f"Device: {device_name}")
                context_parts.append(f"Type: {device_info['type']} ({device_info['model']})")
                context_parts.append(f"Location: {device_info['location']}")
                context_parts.append(f"IP: {device_info['ip']}")
                context_parts.append(f"Protocols: {', '.join(device_info['protocols'])}")
                
                if 'vlans' in device_info:
                    context_parts.append(f"VLANs: {', '.join(device_info['vlans'])}")
                if 'neighbors' in device_info:
                    context_parts.append(f"Connected to: {', '.join(device_info['neighbors'])}")
                
                break
        
        return " | ".join(context_parts) if context_parts else "Standard network"
    
    def get_network_context(self, message):
        """Get relevant network context based on message content"""
        msg = message.lower()
        context_parts = []
        
        # Add topology info
        context_parts.append(f"Network: {self.network_context['network_info']['topology']}")
        
        # Add protocol-specific context
        if 'ospf' in msg:
            context_parts.append(f"OSPF: {self.network_context['network_info']['routing_protocol']}")
        elif 'bgp' in msg:
            context_parts.append(f"BGP: {self.network_context['network_info']['routing_protocol']}")
        elif 'vlan' in msg:
            vlan_info = self.network_context['network_info']['vlans']
            context_parts.append(f"VLANs configured: {', '.join([f'{k}={v}' for k,v in vlan_info.items()])}")
        
        return " | ".join(context_parts)
    
    def get_ai_examples(self, message, intent):
        """Get relevant AI examples for context"""
        msg = message.lower()
        examples = []
        
        # Get examples based on intent and topic
        if intent in self.ai_examples:
            intent_examples = self.ai_examples[intent + "_examples"]
            
            for topic in ['ospf', 'bgp', 'vlan']:
                if topic in msg:
                    for key, example in intent_examples.items():
                        if topic in key:
                            examples.append(f"Example approach: {example}")
                            break
                    break
        
        return examples[0] if examples else ""
    
    def call_openai(self, message, intent, device_context, network_context):
        """Call OpenAI API with rich context"""
        import openai
        client = openai.OpenAI()
        
        # Get relevant examples for context
        example_context = self.get_ai_examples(message, intent)
        
        system_prompt = """You are an expert network engineering assistant with deep knowledge of 
        Cisco networking equipment and protocols. Provide clear, accurate technical guidance for 
        network configuration, troubleshooting, and best practices. Use the provided network context 
        and examples to give specific, actionable advice."""
        
        user_prompt = f"""Network Context: {network_context}

Device Context: {device_context}

{example_context}

User Intent: {intent}
User Message: {message}

Provide specific networking guidance based on the context above. Include commands, explanations, 
and best practices as appropriate."""

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.1
        )
        return response.choices[0].message.content
    
    def chat(self, message):
        """Main chat function with rich context"""
        intent = self.get_intent(message)
        device_context = self.get_device_context(message)
        network_context = self.get_network_context(message)
        
        response = self.call_openai(message, intent, device_context, network_context)
        
        # Store conversation
        self.conversation.append({
            "user": message,
            "response": response,
            "device": self.current_device,
            "intent": intent
        })
        
        return response

# Interactive mode
if __name__ == "__main__":
    print("Network Co-Pilot (OpenAI-powered with Rich Context)")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    try:
        copilot = NetworkCopilot()
        
        # Show available devices
        print("\nAvailable devices:", ", ".join(copilot.devices.keys()))
        print("Try: 'Configure OSPF on R1' or 'Troubleshoot VLAN issues on SW1'\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            
            if not user_input:
                continue
                
            try:
                response = copilot.chat(user_input)
                print(f"\nCo-Pilot: {response}")
                
                if copilot.current_device:
                    device_info = copilot.devices[copilot.current_device]
                    print(f"\n[Working on: {copilot.current_device} - {device_info['type']} at {device_info['location']}]")
                
                print()
                    
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"\nSession ended. Total conversations: {len(copilot.conversation)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please create all required mock_data files first")
    except Exception as e:
        print(f"Setup error: {e}")
        print("Make sure to set OPENAI_API_KEY environment variable")