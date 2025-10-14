#!/usr/bin/env python3
import json
import os
from datetime import datetime
from openai import OpenAI

class NetworkAnalyzerMCPDemo:
    """
    Demonstrates MCP concepts without actual MCP server implementation.
    Shows how network analysis capabilities could be exposed via MCP.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.devices = []
        self.load_network_data()
    
    def load_network_data(self):
        """Load network device data from JSON file"""
        try:
            with open('mock_data/network_metrics.json', 'r') as f:
                data = json.load(f)
                self.devices = data['devices']
            print(f"Loaded data for {len(self.devices)} network devices")
        except FileNotFoundError:
            print("Error: mock_data/network_metrics.json not found")
    
    # MCP Resource Methods (would be exposed as MCP resources)
    
    async def resource_network_health_analysis(self):
        """MCP Resource: network://health-analysis"""
        print("MCP Resource Called: network://health-analysis")
        
        # Prepare device summary for AI
        device_summary = []
        for device in self.devices:
            summary = (f"{device['device_id']} ({device['type']}) at {device['location']}: "
                      f"CPU {device['cpu_percent']}%, Memory {device['memory_percent']}%, "
                      f"Bandwidth {device['bandwidth_percent']}%, Latency {device['latency_ms']}ms, "
                      f"Errors {device['error_rate']}%, Uptime {device['uptime_days']} days")
            device_summary.append(summary)
        
        prompt = f"""You are a senior network engineer analyzing network infrastructure health.

Current Network Status:
{chr(10).join(device_summary)}

Provide a comprehensive analysis including:

1. OVERALL HEALTH STATUS (Healthy/Warning/Critical) with reasoning
2. CRITICAL ISSUES that need immediate attention
3. WARNING CONDITIONS that should be monitored
4. PERFORMANCE OPTIMIZATION opportunities
5. PRIORITIZED ACTION ITEMS for the network team

Focus on practical, actionable insights that a network engineer can implement immediately."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )
            
            result = {
                "mcp_resource": "network://health-analysis",
                "analysis_timestamp": datetime.now().isoformat(),
                "ai_model": "GPT-4",
                "network_summary": {
                    "total_devices": len(self.devices),
                    "data_source": "mock_data/network_metrics.json"
                },
                "ai_analysis": response.choices[0].message.content
            }
            
            return result
            
        except Exception as e:
            return {
                "mcp_resource": "network://health-analysis",
                "error": f"AI analysis failed: {str(e)}",
                "fallback": "Unable to generate AI analysis. Check API configuration."
            }
    
    async def resource_device_status(self):
        """MCP Resource: network://device-status"""
        print("MCP Resource Called: network://device-status")
        
        summary = {
            "mcp_resource": "network://device-status",
            "timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "status_breakdown": {"normal": 0, "warning": 0, "critical": 0},
            "devices": []
        }
        
        for device in self.devices:
            # Simple rule-based status calculation
            status = "normal"
            
            # Warning conditions
            if (device['cpu_percent'] > 70 or device['memory_percent'] > 80 or 
                device['bandwidth_percent'] > 80 or device['latency_ms'] > 15 or 
                device['error_rate'] > 1.0):
                status = "warning"
            
            # Critical conditions
            if (device['cpu_percent'] > 90 or device['memory_percent'] > 95 or 
                device['bandwidth_percent'] > 95 or device['latency_ms'] > 30 or 
                device['error_rate'] > 3.0):
                status = "critical"
            
            summary['status_breakdown'][status] += 1
            summary['devices'].append({
                "device_id": device['device_id'],
                "type": device['type'],
                "location": device['location'],
                "status": status,
                "key_metrics": {
                    "cpu": device['cpu_percent'],
                    "memory": device['memory_percent'],
                    "bandwidth": device['bandwidth_percent'],
                    "latency": device['latency_ms'],
                    "errors": device['error_rate']
                }
            })
        
        return summary
    
    # MCP Tool Methods (would be exposed as MCP tools)
    
    async def tool_analyze_device(self, device_id):
        """MCP Tool: analyze_device"""
        print(f"MCP Tool Called: analyze_device(device_id='{device_id}')")
        
        device = next((d for d in self.devices if d['device_id'] == device_id), None)
        
        if not device:
            return {
                "mcp_tool": "analyze_device", 
                "error": f"Device {device_id} not found"
            }
        
        prompt = f"""You are a network engineer performing detailed device analysis.

Device Details:
- ID: {device['device_id']}
- Type: {device['type']}
- Location: {device['location']}
- CPU Usage: {device['cpu_percent']}%
- Memory Usage: {device['memory_percent']}%
- Bandwidth Utilization: {device['bandwidth_percent']}%
- Latency: {device['latency_ms']}ms
- Error Rate: {device['error_rate']}%
- Uptime: {device['uptime_days']} days

Provide focused analysis:

1. DEVICE STATUS (Normal/Warning/Critical)
2. SPECIFIC ISSUES identified
3. ROOT CAUSE analysis if problems exist
4. IMMEDIATE ACTIONS required (if any)
5. RISK ASSESSMENT (Low/Medium/High)

Be specific about thresholds and {device['type']}-specific considerations."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            
            return {
                "mcp_tool": "analyze_device",
                "device_id": device_id,
                "device_info": device,
                "ai_analysis": response.choices[0].message.content,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "mcp_tool": "analyze_device",
                "error": f"Device analysis failed: {str(e)}"
            }
    
    async def tool_check_critical_devices(self, threshold="critical"):
        """MCP Tool: check_critical_devices"""
        print(f"MCP Tool Called: check_critical_devices(threshold='{threshold}')")
        
        critical_devices = []
        warning_devices = []
        
        for device in self.devices:
            # Apply same logic as status summary
            status = "normal"
            issues = []
            
            if device['cpu_percent'] > 70:
                issues.append(f"High CPU: {device['cpu_percent']}%")
            if device['memory_percent'] > 80:
                issues.append(f"High Memory: {device['memory_percent']}%")
            if device['bandwidth_percent'] > 80:
                issues.append(f"High Bandwidth: {device['bandwidth_percent']}%")
            if device['latency_ms'] > 15:
                issues.append(f"High Latency: {device['latency_ms']}ms")
            if device['error_rate'] > 1.0:
                issues.append(f"High Errors: {device['error_rate']}%")
            
            if issues:
                status = "warning"
            
            # Check for critical conditions
            if (device['cpu_percent'] > 90 or device['memory_percent'] > 95 or 
                device['bandwidth_percent'] > 95 or device['latency_ms'] > 30 or 
                device['error_rate'] > 3.0):
                status = "critical"
            
            device_info = {
                "device_id": device['device_id'],
                "type": device['type'],
                "location": device['location'],
                "status": status,
                "issues": issues
            }
            
            if status == "critical":
                critical_devices.append(device_info)
            elif status == "warning":
                warning_devices.append(device_info)
        
        # Return based on threshold
        if threshold == "critical":
            result_devices = critical_devices
        else:  # threshold == "warning"
            result_devices = critical_devices + warning_devices
        
        return {
            "mcp_tool": "check_critical_devices",
            "threshold": threshold,
            "devices_found": len(result_devices),
            "devices": result_devices,
            "summary": f"Found {len(critical_devices)} critical and {len(warning_devices)} warning devices"
        }

async def main():
    """Demonstrate MCP-style network analysis capabilities"""
    print("AI Network Analyzer - MCP Concepts Demo")
    print("=" * 50)
    print("This demonstrates how network analysis would work via MCP protocol")
    print("=" * 50)
    
    analyzer = NetworkAnalyzerMCPDemo()
    
    # Demonstrate MCP Resources
    print("\n1. MCP RESOURCES:")
    print("-" * 20)
    
    # Test network health analysis resource
    health_result = await analyzer.resource_network_health_analysis()
    if "error" in health_result:
        print(f"Error: {health_result['error']}")
    else:
        print(f"Resource: {health_result['mcp_resource']}")
        print(f"Devices Analyzed: {health_result['network_summary']['total_devices']}")
        print(f"AI Model: {health_result['ai_model']}")
        print("\nAI Analysis:")
        print(health_result['ai_analysis'][:300] + "...")
    
    print(f"\n{'-'*50}")
    
    # Test device status resource
    status_result = await analyzer.resource_device_status()
    print(f"Resource: {status_result['mcp_resource']}")
    print(f"Total Devices: {status_result['total_devices']}")
    breakdown = status_result['status_breakdown']
    print(f"Status Breakdown: {breakdown['normal']} Normal, {breakdown['warning']} Warning, {breakdown['critical']} Critical")
    
    print("\nDevice Status Details:")
    for device in status_result['devices']:
        status_icons = {"normal": "[OK]", "warning": "[WARN]", "critical": "[CRIT]"}
        icon = status_icons[device['status']]
        print(f"  {icon} {device['device_id']} ({device['type']}) - {device['location']}")
    
    # Demonstrate MCP Tools
    print(f"\n\n2. MCP TOOLS:")
    print("-" * 20)
    
    # Test device analysis tool
    device_result = await analyzer.tool_analyze_device("switch-01")
    if "error" in device_result:
        print(f"Error: {device_result['error']}")
    else:
        print(f"Tool: {device_result['mcp_tool']}")
        print(f"Device: {device_result['device_id']}")
        print("AI Analysis:")
        print(device_result['ai_analysis'][:400] + "...")
    
    print(f"\n{'-'*50}")
    
    # Test critical devices tool
    critical_result = await analyzer.tool_check_critical_devices("warning")
    print(f"Tool: {critical_result['mcp_tool']}")
    print(f"Summary: {critical_result['summary']}")
    
    if critical_result['devices']:
        print("Devices Requiring Attention:")
        for device in critical_result['devices']:
            print(f"  - {device['device_id']} ({device['status'].upper()}): {', '.join(device['issues'])}")
    
    print(f"\n{'='*50}")
    print("MCP Demo completed! This shows how the same capabilities")
    print("could be exposed via MCP protocol to AI assistants.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())