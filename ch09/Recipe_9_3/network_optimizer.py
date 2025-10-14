#!/usr/bin/env python3
import json
import os
from datetime import datetime
from openai import OpenAI

class NetworkOptimizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.topology_data = {}
        self.load_topology_data()
    
    def load_topology_data(self):
        """Load network topology and performance data"""
        try:
            with open('mock_data/network_topology.json', 'r') as f:
                self.topology_data = json.load(f)
            
            device_count = len(self.topology_data['devices'])
            print(f"Loaded topology for {device_count} network devices")
            
        except FileNotFoundError:
            print("Error: mock_data/network_topology.json not found")
            exit(1)
    
    def analyze_network_topology(self):
        """KEY: AI topology analysis with optimization focus"""
        devices_summary = []
        bottlenecks = []
        
        for device in self.topology_data['devices']:
            # Device summary with interface details
            interface_info = []
            for interface in device['interfaces']:
                interface_info.append(f"{interface['name']} -> {interface['connected_to']} "
                                    f"({interface['speed_gbps']}Gbps, {interface['utilization']}% used)")
            
            device_summary = (f"{device['device_id']} ({device['type']}, {device['role']}) "
                            f"at {device['location']}: {device['current_utilization']}% utilization, "
                            f"Capacity: {device['capacity_gbps']}Gbps, Redundancy: {device['redundancy']}")
            devices_summary.append(device_summary)
            devices_summary.extend([f"  - {iface}" for iface in interface_info])
            
            # Identify bottlenecks for AI context
            if device['current_utilization'] > 80:
                bottlenecks.append(f"{device['device_id']}: {device['current_utilization']}% utilization")
            
            for interface in device['interfaces']:
                if interface['utilization'] > 85:
                    bottlenecks.append(f"{device['device_id']}.{interface['name']}: {interface['utilization']}% utilization")
        
        issues_summary = [f"{issue['device_id']}: {issue['issue']} (Severity: {issue['severity']})" 
                         for issue in self.topology_data.get('performance_issues', [])]
        
        # KEY: Comprehensive optimization prompt
        prompt = f"""You are a senior network architect analyzing network topology for optimization opportunities.

NETWORK TOPOLOGY ANALYSIS:
Network: {self.topology_data['metadata']['network_name']}
Total Devices: {len(self.topology_data['devices'])}

DEVICE TOPOLOGY:
{chr(10).join(devices_summary)}

IDENTIFIED BOTTLENECKS:
{chr(10).join(bottlenecks) if bottlenecks else "No significant bottlenecks detected"}

CURRENT PERFORMANCE ISSUES:
{chr(10).join(issues_summary) if issues_summary else "No reported performance issues"}

Provide comprehensive topology analysis:
1. TOPOLOGY STRENGTHS and design advantages
2. CRITICAL BOTTLENECKS and single points of failure
3. REDUNDANCY ASSESSMENT and resilience gaps
4. CAPACITY PLANNING priorities
5. OPTIMIZATION RECOMMENDATIONS with specific implementation steps:
   - Interface upgrades needed
   - Load balancing improvements
   - Redundancy enhancements
   - QoS optimizations
6. RISK ASSESSMENT for each recommendation
7. IMPLEMENTATION PRIORITY (High/Medium/Low) and timeline

Focus on practical, implementable solutions that improve performance and reliability."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=900,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Topology analysis failed: {str(e)}"

def main():
    print("AI-Powered Network Optimization")
    print("=" * 40)
    
    optimizer = NetworkOptimizer()
    
    # Overall topology analysis
    print("NETWORK TOPOLOGY ANALYSIS")
    print("=" * 30)
    topology_analysis = optimizer.analyze_network_topology()
    print(topology_analysis)

if __name__ == "__main__":
    main()