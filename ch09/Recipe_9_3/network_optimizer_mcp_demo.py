#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

class NetworkOptimizerMCPDemo:
    """
    Demonstrates advanced MCP concepts for network optimization:
    - Tool chaining: Multi-step optimization workflows
    - Security models: Permission validation for network changes
    - Complex workflows: Multi-stage processes with dependencies
    - Integration patterns: Change management system integration
    """
    
    def __init__(self, user_permissions=None):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Security model: User permissions for different operations
        self.user_permissions = user_permissions or {
            "network_read": True,
            "network_analyze": True,
            "network_admin": False,  # Default: no admin permissions
            "change_management": False
        }
    
    def load_topology_data(self):
        """Load network topology data following stateless pattern"""
        try:
            with open('mock_data/network_topology.json', 'r') as f:
                data = json.load(f)
            print(f"Fresh topology data loaded: {len(data['devices'])} devices")
            return data
        except FileNotFoundError:
            return None
    
    def check_permission(self, required_permission):
        """Security model: Check user permissions for operations"""
        return self.user_permissions.get(required_permission, False)
    
    # ===============================
    # MCP RESOURCES - Network Intelligence
    # ===============================
    
    async def resource_topology_analysis(self):
        """
        MCP Resource: network://topology-analysis
        
        Demonstrates:
        - Security model: Permission checking for network access
        - Complex data processing: Multi-device topology analysis
        - Structured intelligence: Organized optimization insights
        """
        print("MCP Resource Called: network://topology-analysis")
        
        # Security model: Check permissions
        if not self.check_permission("network_read"):
            return {
                "mcp_resource": "network://topology-analysis",
                "error": "Insufficient permissions",
                "required_permission": "network_read",
                "current_permissions": list(self.user_permissions.keys())
            }
        
        topology_data = self.load_topology_data()
        if not topology_data:
            return {
                "mcp_resource": "network://topology-analysis",
                "error": "Topology data not available",
                "fallback": "Use manual network documentation"
            }
        
        # Complex data processing: Analyze topology structure
        analysis_result = {
            "mcp_resource": "network://topology-analysis",
            "analysis_timestamp": datetime.now().isoformat(),
            "network_metadata": topology_data['metadata'],
            "topology_summary": {
                "total_devices": len(topology_data['devices']),
                "device_types": {},
                "redundancy_analysis": {},
                "bottleneck_summary": {}
            },
            "optimization_opportunities": []
        }
        
        # Analyze device types and roles
        for device in topology_data['devices']:
            device_type = device['type']
            if device_type not in analysis_result['topology_summary']['device_types']:
                analysis_result['topology_summary']['device_types'][device_type] = 0
            analysis_result['topology_summary']['device_types'][device_type] += 1
            
            # Redundancy analysis
            redundancy = device['redundancy']
            if redundancy not in analysis_result['topology_summary']['redundancy_analysis']:
                analysis_result['topology_summary']['redundancy_analysis'][redundancy] = []
            analysis_result['topology_summary']['redundancy_analysis'][redundancy].append(device['device_id'])
            
            # Bottleneck identification
            if device['current_utilization'] > 80:
                analysis_result['topology_summary']['bottleneck_summary'][device['device_id']] = {
                    "utilization": device['current_utilization'],
                    "type": device['type'],
                    "location": device['location']
                }
        
        # Identify optimization opportunities
        single_points = analysis_result['topology_summary']['redundancy_analysis'].get('none', [])
        if single_points:
            analysis_result['optimization_opportunities'].append({
                "category": "redundancy",
                "priority": "high",
                "description": f"Add redundancy for {len(single_points)} devices with no backup",
                "affected_devices": single_points
            })
        
        high_util_devices = [d for d in topology_data['devices'] if d['current_utilization'] > 85]
        if high_util_devices:
            analysis_result['optimization_opportunities'].append({
                "category": "capacity",
                "priority": "medium",
                "description": f"Upgrade capacity for {len(high_util_devices)} overloaded devices",
                "affected_devices": [d['device_id'] for d in high_util_devices]
            })
        
        return analysis_result
    
    async def resource_optimization_recommendations(self):
        """
        MCP Resource: network://optimization-recommendations
        
        Demonstrates:
        - Resource composition: Using topology analysis + performance data
        - Business logic integration: Priority and impact assessment
        - Structured recommendations: Actionable optimization guidance
        """
        print("MCP Resource Called: network://optimization-recommendations")
        
        if not self.check_permission("network_analyze"):
            return {
                "mcp_resource": "network://optimization-recommendations",
                "error": "Insufficient permissions for analysis",
                "required_permission": "network_analyze"
            }
        
        # Resource composition: Use topology analysis
        topology_analysis = await self.resource_topology_analysis()
        if "error" in topology_analysis:
            return {
                "mcp_resource": "network://optimization-recommendations",
                "error": "Cannot generate recommendations without topology data",
                "dependency_error": topology_analysis["error"]
            }
        
        topology_data = self.load_topology_data()
        
        recommendations = {
            "mcp_resource": "network://optimization-recommendations",
            "generated_at": datetime.now().isoformat(),
            "recommendation_categories": {
                "immediate": [],
                "short_term": [],
                "long_term": []
            },
            "total_recommendations": 0,
            "estimated_total_cost": 0
        }
        
        # Process optimization opportunities from topology analysis
        for opportunity in topology_analysis.get('optimization_opportunities', []):
            if opportunity['priority'] == 'high':
                category = "immediate"
                timeline = "0-30 days"
                estimated_cost = 50000  # High priority items
            elif opportunity['priority'] == 'medium':
                category = "short_term"
                timeline = "1-3 months"
                estimated_cost = 25000  # Medium priority items
            else:
                category = "long_term"
                timeline = "3-12 months"
                estimated_cost = 15000  # Lower priority items
            
            recommendation = {
                "category": opportunity['category'],
                "description": opportunity['description'],
                "affected_devices": opportunity['affected_devices'],
                "timeline": timeline,
                "estimated_cost": estimated_cost,
                "business_impact": "High" if opportunity['priority'] == 'high' else "Medium",
                "implementation_complexity": "Medium"
            }
            
            recommendations['recommendation_categories'][category].append(recommendation)
            recommendations['estimated_total_cost'] += estimated_cost
        
        recommendations['total_recommendations'] = sum(
            len(recs) for recs in recommendations['recommendation_categories'].values()
        )
        
        return recommendations
    
    # ===============================
    # MCP TOOLS - Optimization Workflows
    # ===============================
    
    async def tool_generate_optimization_plan(self, focus_area="performance", urgency="normal"):
        """
        MCP Tool: generate_optimization_plan
        
        Demonstrates:
        - Tool chaining: Uses multiple resources and tools
        - Complex workflows: Multi-step optimization planning
        - Input validation: Comprehensive parameter checking
        """
        print(f"MCP Tool Called: generate_optimization_plan(focus='{focus_area}', urgency='{urgency}')")
        
        # Input validation
        valid_focus_areas = ["performance", "redundancy", "capacity", "security", "all"]
        valid_urgencies = ["low", "normal", "high", "critical"]
        
        if focus_area not in valid_focus_areas:
            return {
                "mcp_tool": "generate_optimization_plan",
                "error": f"Invalid focus_area: {focus_area}",
                "valid_options": valid_focus_areas
            }
        
        if urgency not in valid_urgencies:
            return {
                "mcp_tool": "generate_optimization_plan",
                "error": f"Invalid urgency: {urgency}",
                "valid_options": valid_urgencies
            }
        
        # Security model: Check permissions
        if not self.check_permission("network_analyze"):
            return {
                "mcp_tool": "generate_optimization_plan",
                "error": "Insufficient permissions for optimization planning",
                "required_permission": "network_analyze"
            }
        
        # Tool chaining: Use multiple resources
        topology_analysis = await self.resource_topology_analysis()
        recommendations = await self.resource_optimization_recommendations()
        
        if "error" in topology_analysis or "error" in recommendations:
            return {
                "mcp_tool": "generate_optimization_plan",
                "error": "Cannot generate plan due to data access issues",
                "dependencies": ["topology_analysis", "optimization_recommendations"]
            }
        
        # Generate AI-powered optimization plan
        bottlenecks = topology_analysis.get('topology_summary', {}).get('bottleneck_summary', {})
        opportunities = recommendations.get('recommendation_categories', {})
        
        # Prepare context for AI
        context_summary = f"""
        Network: {topology_analysis['network_metadata']['network_name']}
        Focus Area: {focus_area}
        Urgency Level: {urgency}
        
        Current Bottlenecks: {list(bottlenecks.keys()) if bottlenecks else 'None detected'}
        Immediate Actions Needed: {len(opportunities.get('immediate', []))}
        Short-term Projects: {len(opportunities.get('short_term', []))}
        """
        
        prompt = f"""You are a network optimization specialist creating a comprehensive implementation plan.

{context_summary}

Current Network Issues:
{json.dumps(bottlenecks, indent=2) if bottlenecks else 'No critical bottlenecks identified'}

Available Optimization Opportunities:
{json.dumps(opportunities, indent=2)}

Create a detailed optimization plan focused on {focus_area} with {urgency} urgency:

1. EXECUTIVE SUMMARY (business impact and ROI)
2. IMMEDIATE ACTIONS (0-30 days):
   - Critical fixes and emergency optimizations
   - Resource requirements and timeline
3. SHORT-TERM IMPROVEMENTS (1-3 months):
   - Strategic optimizations and capacity additions
   - Implementation dependencies and risks
4. LONG-TERM STRATEGIC CHANGES (3-12 months):
   - Architecture improvements and technology refresh
   - Scalability and future-proofing considerations
5. RISK MITIGATION:
   - Implementation risks and mitigation strategies
   - Rollback procedures and testing requirements
6. SUCCESS METRICS:
   - KPIs to measure optimization effectiveness
   - Monitoring and validation procedures

Focus on {focus_area} optimization while considering network stability and business continuity."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            return {
                "mcp_tool": "generate_optimization_plan",
                "focus_area": focus_area,
                "urgency": urgency,
                "plan_generated_at": datetime.now().isoformat(),
                "optimization_plan": response.choices[0].message.content,
                "data_sources": ["topology_analysis", "optimization_recommendations"],
                "ai_model": "GPT-4",
                "plan_validity": "30 days"
            }
            
        except Exception as e:
            return {
                "mcp_tool": "generate_optimization_plan",
                "error": f"Plan generation failed: {str(e)}",
                "fallback": "Use manual optimization planning procedures"
            }
    
    async def tool_create_change_request(self, optimization_id, target_devices, estimated_downtime="none"):
        """
        MCP Tool: create_change_request
        
        Demonstrates:
        - Security model: Admin permissions required for changes
        - Integration patterns: Change management system integration
        - Complex workflows: Multi-step approval and implementation
        """
        print(f"MCP Tool Called: create_change_request(optimization='{optimization_id}')")
        
        # Security model: Require admin permissions for change requests
        if not self.check_permission("change_management"):
            return {
                "mcp_tool": "create_change_request",
                "error": "Insufficient permissions for change management",
                "required_permission": "change_management",
                "escalation": "Contact network operations manager for approval"
            }
        
        # Input validation
        if not optimization_id:
            return {
                "mcp_tool": "create_change_request",
                "error": "optimization_id is required",
                "example": "interface_upgrade_edge_switch_01"
            }
        
        if not target_devices or not isinstance(target_devices, list):
            return {
                "mcp_tool": "create_change_request",
                "error": "target_devices must be a non-empty list",
                "example": ["edge-switch-01", "core-router-01"]
            }
        
        # Validate devices exist in topology
        topology_data = self.load_topology_data()
        if topology_data:
            valid_devices = [d['device_id'] for d in topology_data['devices']]
            invalid_devices = [d for d in target_devices if d not in valid_devices]
            if invalid_devices:
                return {
                    "mcp_tool": "create_change_request",
                    "error": f"Invalid devices specified: {invalid_devices}",
                    "valid_devices": valid_devices
                }
        
        # Complex workflow: Generate change request with approval workflow
        change_request = {
            "mcp_tool": "create_change_request",
            "change_id": f"CHG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "optimization_id": optimization_id,
            "created_at": datetime.now().isoformat(),
            "status": "pending_approval",
            "details": {
                "target_devices": target_devices,
                "estimated_downtime": estimated_downtime,
                "implementation_window": self.calculate_maintenance_window(),
                "risk_level": self.assess_change_risk(target_devices, estimated_downtime),
                "rollback_plan": "Available - configuration snapshots and interface rollback procedures",
                "testing_requirements": ["Pre-change connectivity tests", "Post-change performance validation"]
            },
            "approval_workflow": {
                "required_approvers": ["network_manager", "change_advisory_board"],
                "current_step": "manager_review",
                "approval_deadline": (datetime.now() + timedelta(days=3)).isoformat()
            },
            "implementation_checklist": [
                "Schedule maintenance window",
                "Notify affected users",
                "Prepare rollback procedures",
                "Execute change",
                "Validate functionality",
                "Update documentation"
            ]
        }
        
        return change_request
    
    async def tool_execute_optimization_workflow(self, change_id, step="validate"):
        """
        MCP Tool: execute_optimization_workflow
        
        Demonstrates:
        - Tool chaining: Multi-step workflow execution
        - State management: Workflow step tracking
        - Error handling: Comprehensive failure scenarios
        """
        print(f"MCP Tool Called: execute_optimization_workflow(change_id='{change_id}', step='{step}')")
        
        valid_steps = ["validate", "approve", "schedule", "implement", "verify", "close"]
        if step not in valid_steps:
            return {
                "mcp_tool": "execute_optimization_workflow",
                "error": f"Invalid workflow step: {step}",
                "valid_steps": valid_steps,
                "current_step_description": {
                    "validate": "Pre-implementation validation and testing",
                    "approve": "Management and CAB approval",
                    "schedule": "Schedule implementation window",
                    "implement": "Execute the optimization changes",
                    "verify": "Post-implementation verification",
                    "close": "Close change request and update documentation"
                }
            }
        
        # Security model: Different permissions for different steps
        required_permissions = {
            "validate": "network_analyze",
            "approve": "change_management", 
            "schedule": "change_management",
            "implement": "network_admin",
            "verify": "network_analyze",
            "close": "change_management"
        }
        
        if not self.check_permission(required_permissions[step]):
            return {
                "mcp_tool": "execute_optimization_workflow",
                "error": f"Insufficient permissions for step: {step}",
                "required_permission": required_permissions[step]
            }
        
        # Simulate workflow execution based on step
        workflow_result = {
            "mcp_tool": "execute_optimization_workflow",
            "change_id": change_id,
            "step_executed": step,
            "execution_timestamp": datetime.now().isoformat(),
            "result": "success",
            "details": {}
        }
        
        if step == "validate":
            workflow_result["details"] = {
                "validation_checks": [
                    {"check": "Device connectivity", "status": "passed"},
                    {"check": "Configuration backup", "status": "passed"},
                    {"check": "Resource availability", "status": "passed"}
                ],
                "next_step": "approve",
                "validation_summary": "All pre-implementation checks passed"
            }
        elif step == "implement":
            workflow_result["details"] = {
                "implementation_steps": [
                    {"step": "Create configuration snapshot", "status": "completed", "duration": "30s"},
                    {"step": "Apply optimization changes", "status": "completed", "duration": "120s"},
                    {"step": "Restart affected services", "status": "completed", "duration": "45s"}
                ],
                "total_duration": "195s",
                "next_step": "verify",
                "implementation_summary": "Optimization changes applied successfully"
            }
        elif step == "verify":
            workflow_result["details"] = {
                "verification_tests": [
                    {"test": "Interface utilization check", "result": "Improved by 25%"},
                    {"test": "Connectivity verification", "result": "All paths operational"},
                    {"test": "Performance baseline", "result": "Latency reduced by 15%"}
                ],
                "next_step": "close",
                "verification_summary": "Optimization objectives achieved"
            }
        
        return workflow_result
    
    def calculate_maintenance_window(self):
        """Helper: Calculate optimal maintenance window"""
        # Typically schedule for early morning hours
        next_maintenance = datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
        if next_maintenance <= datetime.now():
            next_maintenance += timedelta(days=1)
        
        return {
            "start_time": next_maintenance.isoformat(),
            "end_time": (next_maintenance + timedelta(hours=4)).isoformat(),
            "duration_hours": 4,
            "timezone": "UTC"
        }
    
    def assess_change_risk(self, target_devices, estimated_downtime):
        """Helper: Assess risk level for network changes"""
        if estimated_downtime != "none":
            return "high"
        elif len(target_devices) > 3:
            return "medium"
        else:
            return "low"

async def main():
    """Demonstrate advanced MCP concepts for network optimization"""
    print("AI Network Optimizer - Advanced MCP Concepts Demo")
    print("=" * 60)
    print("Demonstrates: Tool Chaining, Security Models, Complex Workflows, Integration Patterns")
    print("=" * 60)
    
    # Initialize with different permission levels for demonstration
    optimizer_admin = NetworkOptimizerMCPDemo({
        "network_read": True,
        "network_analyze": True,
        "network_admin": True,
        "change_management": True
    })
    
    optimizer_readonly = NetworkOptimizerMCPDemo({
        "network_read": True,
        "network_analyze": False,
        "network_admin": False,
        "change_management": False
    })
    
    # ===============================
    # DEMONSTRATE SECURITY MODELS
    # ===============================
    print("\n1. MCP SECURITY MODELS (Permission-Based Access Control):")
    print("-" * 60)
    
    # Test with admin permissions
    print("Testing with ADMIN permissions:")
    topology_analysis = await optimizer_admin.resource_topology_analysis()
    print(f"Resource: {topology_analysis['mcp_resource']}")
    print(f"Network: {topology_analysis['network_metadata']['network_name']}")
    print(f"Total Devices: {topology_analysis['topology_summary']['total_devices']}")
    
    bottlenecks = topology_analysis['topology_summary']['bottleneck_summary']
    if bottlenecks:
        print(f"Bottlenecks Detected: {list(bottlenecks.keys())}")
    
    # Test with read-only permissions
    print(f"\nTesting with READ-ONLY permissions:")
    readonly_result = await optimizer_readonly.resource_topology_analysis()
    if "error" in readonly_result:
        print(f"Access Denied: {readonly_result['error']}")
        print(f"Required Permission: {readonly_result['required_permission']}")
    
    # ===============================
    # DEMONSTRATE RESOURCE COMPOSITION
    # ===============================
    print(f"\n\n2. MCP RESOURCE COMPOSITION (Multi-Source Intelligence):")
    print("-" * 60)
    
    # Generate optimization recommendations (uses topology analysis)
    recommendations = await optimizer_admin.resource_optimization_recommendations()
    print(f"Resource: {recommendations['mcp_resource']}")
    print(f"Total Recommendations: {recommendations['total_recommendations']}")
    print(f"Estimated Total Cost: ${recommendations['estimated_total_cost']:,}")
    
    for category, recs in recommendations['recommendation_categories'].items():
        if recs:
            print(f"\n{category.upper()} Actions ({len(recs)} items):")
            for rec in recs:
                print(f"  - {rec['description']}")
                print(f"    Timeline: {rec['timeline']}, Cost: ${rec['estimated_cost']:,}")
    
    # ===============================
    # DEMONSTRATE TOOL CHAINING
    # ===============================
    print(f"\n\n3. MCP TOOL CHAINING (Multi-Step Workflows):")
    print("-" * 50)
    
    # Generate comprehensive optimization plan (uses multiple resources)
    optimization_plan = await optimizer_admin.tool_generate_optimization_plan("performance", "high")
    if "error" not in optimization_plan:
        print(f"Tool: {optimization_plan['mcp_tool']}")
        print(f"Focus: {optimization_plan['focus_area']}, Urgency: {optimization_plan['urgency']}")
        print(f"AI Model: {optimization_plan['ai_model']}")
        
        print(f"\nOptimization Plan Summary:")
        plan_text = optimization_plan['optimization_plan']
        print(plan_text[:600] + "..." if len(plan_text) > 600 else plan_text)
    
    # ===============================
    # DEMONSTRATE COMPLEX WORKFLOWS
    # ===============================
    print(f"\n\n4. MCP COMPLEX WORKFLOWS (Change Management Integration):")
    print("-" * 65)
    
    # Create change request (requires admin permissions)
    change_request = await optimizer_admin.tool_create_change_request(
        "interface_upgrade_edge_switch_01", 
        ["edge-switch-01"], 
        "2 hours"
    )
    
    if "error" not in change_request:
        print(f"Tool: {change_request['mcp_tool']}")
        print(f"Change ID: {change_request['change_id']}")
        print(f"Status: {change_request['status']}")
        print(f"Risk Level: {change_request['details']['risk_level']}")
        
        workflow = change_request['approval_workflow']
        print(f"Current Step: {workflow['current_step']}")
        print(f"Required Approvers: {', '.join(workflow['required_approvers'])}")
        
        # Demonstrate workflow execution
        print(f"\nExecuting Workflow Steps:")
        
        # Step 1: Validate
        validate_result = await optimizer_admin.tool_execute_optimization_workflow(
            change_request['change_id'], "validate"
        )
        if "error" not in validate_result:
            print(f"  1. Validation: {validate_result['details']['validation_summary']}")
        
        # Step 2: Implementation (simulation)
        implement_result = await optimizer_admin.tool_execute_optimization_workflow(
            change_request['change_id'], "implement"
        )
        if "error" not in implement_result:
            print(f"  2. Implementation: {implement_result['details']['implementation_summary']}")
            print(f"     Duration: {implement_result['details']['total_duration']}")
        
        # Step 3: Verification
        verify_result = await optimizer_admin.tool_execute_optimization_workflow(
            change_request['change_id'], "verify"
        )
        if "error" not in verify_result:
            print(f"  3. Verification: {verify_result['details']['verification_summary']}")
    
    # ===============================
    # DEMONSTRATE PERMISSION VALIDATION
    # ===============================
    print(f"\n\n5. MCP SECURITY VALIDATION (Permission Enforcement):")
    print("-" * 55)
    
    # Test readonly user trying to create change request
    readonly_change = await optimizer_readonly.tool_create_change_request(
        "test_change", ["router-01"]
    )
    print(f"Read-only user attempting change request:")
    print(f"  Result: {readonly_change['error']}")
    print(f"  Required Permission: {readonly_change['required_permission']}")
    print(f"  Escalation: {readonly_change['escalation']}")
    
    # Test readonly user trying workflow execution
    readonly_workflow = await optimizer_readonly.tool_execute_optimization_workflow(
        "CHG-123", "implement"
    )
    print(f"\nRead-only user attempting workflow execution:")
    print(f"  Result: {readonly_workflow['error']}")
    print(f"  Required Permission: {readonly_workflow['required_permission']}")
    
    # ===============================
    # MCP CONCEPTS SUMMARY
    # ===============================
    print(f"\n{'='*60}")
    print("ADVANCED MCP CONCEPTS DEMONSTRATED:")
    print("=" * 60)
    print("Tool Chaining: Multi-step optimization workflows using multiple resources")
    print("Security Models: Role-based permissions for different network operations")
    print("Complex Workflows: Multi-stage change management with approval processes")
    print("Integration Patterns: Change management system integration and workflows")
    print("Permission Validation: Granular access control for network modifications")
    print("State Management: Workflow step tracking and validation")
    print("Error Handling: Comprehensive failure scenarios and permission checks")
    print("Business Logic: Change risk assessment and maintenance window scheduling")
    print("\nThis demonstrates enterprise-grade MCP servers for network")
    print("operations with proper security, workflows, and integration!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())