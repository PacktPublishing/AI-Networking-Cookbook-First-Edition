#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

class NetworkPerformancePredictor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.time_series_data = {}
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical network performance data"""
        try:
            with open('mock_data/time_series.json', 'r') as f:
                self.time_series_data = json.load(f)
            
            device_count = len(self.time_series_data) - 1  # Exclude metadata
            period = self.time_series_data['metadata']['collection_period']
            print(f"Loaded {period} of historical data for {device_count} devices")
            
        except FileNotFoundError:
            print("Error: mock_data/time_series.json not found")
            exit(1)
    
    def analyze_performance_trends(self, device_id):
        """KEY: AI-powered trend analysis with statistical context"""
        if device_id not in self.time_series_data:
            return f"No historical data available for {device_id}"
        
        device_data = self.time_series_data[device_id]
        bw_data = device_data['bandwidth_utilization']
        
        # Statistical context for AI
        bw_avg = sum(bw_data) / len(bw_data)
        bw_max = max(bw_data)
        first_half_avg = sum(bw_data[:len(bw_data)//2]) / (len(bw_data)//2)
        second_half_avg = sum(bw_data[len(bw_data)//2:]) / (len(bw_data) - len(bw_data)//2)
        trend_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        # Recent performance (last 24 hours)
        recent_bw = bw_data[-24:] if len(bw_data) >= 24 else bw_data
        recent_avg = sum(recent_bw) / len(recent_bw)
        
        # KEY: Structured prompt with statistical context
        prompt = f"""You are a network performance analyst examining historical data trends.

Device: {device_id}
Analysis Period: {self.time_series_data['metadata']['collection_period']}
Data Points: {len(bw_data)} hourly measurements

BANDWIDTH UTILIZATION ANALYSIS:
- Average: {bw_avg:.1f}%
- Peak: {bw_max:.1f}%
- Recent 24h Average: {recent_avg:.1f}%
- Trend: {trend_change:+.1f}% change from first half to second half of period

SAMPLE DATA POINTS (recent bandwidth %):
{recent_bw[-12:]}

Based on this performance data, provide analysis:
1. PERFORMANCE TREND ASSESSMENT (Improving/Stable/Degrading)
2. CAPACITY UTILIZATION PATTERNS (peak hours, usage cycles)
3. PERFORMANCE PREDICTIONS for next 24-48 hours
4. CAPACITY PLANNING RECOMMENDATIONS
5. POTENTIAL ISSUES to monitor
6. OPTIMIZATION OPPORTUNITIES

Focus on actionable insights for network capacity planning."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Trend analysis failed: {str(e)}"

def main():
    print("AI-Powered Network Performance Prediction")
    print("=" * 55)
    
    predictor = NetworkPerformancePredictor()
    
    # Analyze trends for available devices
    devices = [d for d in predictor.time_series_data.keys() if d != 'metadata']
    
    for device_id in devices[:2]:  # Analyze first 2 devices
        print(f"\nAnalyzing performance trends for {device_id}...")
        print("=" * 40)
        
        trend_analysis = predictor.analyze_performance_trends(device_id)
        print("PERFORMANCE TREND ANALYSIS:")
        print("-" * 25)
        print(trend_analysis)

if __name__ == "__main__":
    main()