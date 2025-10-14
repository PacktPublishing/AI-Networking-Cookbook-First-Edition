#!/usr/bin/env python3
import json
import os
from datetime import datetime
from openai import OpenAI

class AINetworkAnalyzer:
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
            exit(1)
    
    def analyze_network_health(self):
        """Use AI to analyze overall network health"""
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

Focus on practical, actionable insights that a network engineer can implement immediately.
Consider device types, locations, and interdependencies in your analysis."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI analysis failed: {str(e)}"
    
    def analyze_device(self, device_id):
        """Analyze a specific device with AI"""
        device = next((d for d in self.devices if d['device_id'] == device_id), None)
        
        if not device:
            return f"Device {device_id} not found"
        
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
- Interfaces: {device['interface_count']}
- Active Connections: {device['active_connections']}

Provide focused analysis:

1. DEVICE STATUS (Normal/Warning/Critical)
2. SPECIFIC ISSUES identified
3. ROOT CAUSE analysis if problems exist
4. IMMEDIATE ACTIONS required (if any)
5. RISK ASSESSMENT (Low/Medium/High)
6. RECOMMENDED MONITORING for this device

Be specific about thresholds, expected performance, and {device['type']}-specific considerations."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Device analysis failed: {str(e)}"
    
    def get_device_status_summary(self):
        """Generate simple status summary for all devices"""
        summary = {
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
                    "bandwidth": device['bandwidth_percent'],
                    "latency": device['latency_ms']
                }
            })
        
        return summary

def main():
    """Main function to demonstrate AI network analysis"""
    print("AI-Powered Network Health Analysis")
    print("=" * 50)
    
    analyzer = AINetworkAnalyzer()
    
    # Overall network health analysis
    print("Analyzing overall network health...")
    health_analysis = analyzer.analyze_network_health()
    print("\nAI NETWORK HEALTH ANALYSIS:")
    print("-" * 30)
    print(health_analysis)
    
    # Device status summary
    print("\n" + "=" * 50)
    print("DEVICE STATUS SUMMARY:")
    print("-" * 30)
    status_summary = analyzer.get_device_status_summary()
    
    print(f"Total Devices: {status_summary['total_devices']}")
    print(f"Normal: {status_summary['status_breakdown']['normal']}")
    print(f"Warning: {status_summary['status_breakdown']['warning']}")
    print(f"Critical: {status_summary['status_breakdown']['critical']}")
    
    print("\nDevice Details:")
    for device in status_summary['devices']:
        status_icon = {"normal": "[OK]", "warning": "[WARN]", "critical": "[CRIT]"}
        print(f"  {status_icon[device['status']]} {device['device_id']} ({device['type']}) - {device['location']}")
    
    # Detailed analysis of critical devices
    critical_devices = [d for d in status_summary['devices'] if d['status'] == 'critical']
    if critical_devices:
        print("\n" + "=" * 50)
        print("DETAILED ANALYSIS OF CRITICAL DEVICES:")
        print("-" * 30)
        
        for device in critical_devices:
            print(f"\nAnalyzing {device['device_id']}...")
            device_analysis = analyzer.analyze_device(device['device_id'])
            print(f"\nAI ANALYSIS - {device['device_id']}:")
            print("-" * 20)
            print(device_analysis)

if __name__ == "__main__":
    main()