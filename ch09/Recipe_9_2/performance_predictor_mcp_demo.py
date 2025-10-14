#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI

class PerformancePredictorMCPDemo:
    """
    Demonstrates intermediate MCP concepts for time-series analysis:
    - State management (stateless time-series processing)
    - Data handling (efficient historical data processing)
    - Error patterns (robust data processing error handling)
    - Resource composition (combining multiple data sources)
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Note: No persistent state - following MCP stateless design
    
    def load_time_series_data(self):
        """
        MCP State Management: Load fresh data for each request
        
        Demonstrates:
        - Stateless design: No reliance on instance variables
        - Fresh data loading: Each MCP request gets current data
        - Error handling: Graceful failure if data unavailable
        """
        try:
            with open('mock_data/time_series.json', 'r') as f:
                data = json.load(f)
            print(f"Fresh data loaded: {data['metadata']['collection_period']} for {len(data)-1} devices")
            return data
        except FileNotFoundError:
            return None
    
    # ===============================
    # MCP RESOURCES - Time Series Data
    # ===============================
    
    async def resource_performance_trends(self):
        """
        MCP Resource: network://performance-trends
        
        Demonstrates:
        - Data size considerations: Summarized time-series data
        - Resource composition: Multiple device data combined
        - Efficient data handling: Statistics vs raw data
        """
        print("MCP Resource Called: network://performance-trends")
        
        # MCP State Management: Load fresh data
        time_series_data = self.load_time_series_data()
        if not time_series_data:
            return {
                "mcp_resource": "network://performance-trends",
                "error": "Historical data not available",
                "fallback": "Use current metrics only for analysis",
                "data_source": "mock_data/time_series.json"
            }
        
        trends_summary = {
            "mcp_resource": "network://performance-trends",
            "analysis_timestamp": datetime.now().isoformat(),
            "data_period": time_series_data['metadata']['collection_period'],
            "device_trends": {},
            "network_summary": {
                "total_devices": len(time_series_data) - 1,
                "data_points_per_device": len(list(time_series_data.values())[1]['bandwidth_utilization'])
            }
        }
        
        # Process each device's performance data
        for device_id, device_data in time_series_data.items():
            if device_id == 'metadata':
                continue
                
            bw_data = device_data['bandwidth_utilization']
            
            # Calculate key statistics (data size consideration)
            avg_utilization = sum(bw_data) / len(bw_data)
            peak_utilization = max(bw_data)
            
            # Trend calculation
            first_half_avg = sum(bw_data[:len(bw_data)//2]) / (len(bw_data)//2)
            second_half_avg = sum(bw_data[len(bw_data)//2:]) / (len(bw_data) - len(bw_data)//2)
            trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
            
            # Recent performance pattern
            recent_data = bw_data[-24:] if len(bw_data) >= 24 else bw_data
            
            trends_summary['device_trends'][device_id] = {
                "average_utilization": round(avg_utilization, 1),
                "peak_utilization": round(peak_utilization, 1),
                "trend_direction": "increasing" if trend_percentage > 2 else "decreasing" if trend_percentage < -2 else "stable",
                "trend_percentage": round(trend_percentage, 1),
                "recent_pattern": recent_data[-12:],  # Last 12 hours sample
                "capacity_status": "critical" if peak_utilization > 90 else "warning" if peak_utilization > 80 else "normal"
            }
        
        return trends_summary
    
    async def resource_capacity_forecast(self):
        """
        MCP Resource: network://capacity-forecast
        
        Demonstrates:
        - Error handling patterns: Multiple failure modes handled
        - Data processing robustness: Handles missing or corrupt data
        - Structured error responses: Detailed error context
        """
        print("MCP Resource Called: network://capacity-forecast")
        
        time_series_data = self.load_time_series_data()
        if not time_series_data:
            return {
                "mcp_resource": "network://capacity-forecast",
                "error": "Cannot generate forecast without historical data",
                "error_type": "data_unavailable",
                "fallback": "Use manual capacity planning procedures",
                "required_data": "7 days of hourly performance metrics"
            }
        
        try:
            forecast_summary = {
                "mcp_resource": "network://capacity-forecast",
                "forecast_timestamp": datetime.now().isoformat(),
                "forecast_horizon": "7_days",
                "device_forecasts": {},
                "network_alerts": []
            }
            
            for device_id, device_data in time_series_data.items():
                if device_id == 'metadata':
                    continue
                
                # Error handling: Check data completeness
                if 'bandwidth_utilization' not in device_data:
                    forecast_summary['device_forecasts'][device_id] = {
                        "error": "Missing bandwidth utilization data",
                        "status": "forecast_unavailable"
                    }
                    continue
                
                bw_data = device_data['bandwidth_utilization']
                
                # Error handling: Validate data quality
                if len(bw_data) < 24:
                    forecast_summary['device_forecasts'][device_id] = {
                        "error": f"Insufficient data points: {len(bw_data)} (minimum 24 required)",
                        "status": "insufficient_data"
                    }
                    continue
                
                # Generate forecast for this device
                recent_avg = sum(bw_data[-24:]) / 24
                weekly_growth = ((sum(bw_data[-24:]) / 24) - (sum(bw_data[:24]) / 24)) / (sum(bw_data[:24]) / 24) * 100
                
                # Capacity projection
                days_to_80_percent = None
                if recent_avg < 80 and weekly_growth > 0:
                    days_to_80_percent = int((80 - recent_avg) / (weekly_growth / 7))
                
                forecast_summary['device_forecasts'][device_id] = {
                    "current_avg_utilization": round(recent_avg, 1),
                    "weekly_growth_rate": round(weekly_growth, 2),
                    "projected_utilization_7d": round(recent_avg + weekly_growth, 1),
                    "days_to_80_percent": days_to_80_percent,
                    "capacity_alert": recent_avg > 70 or (days_to_80_percent and days_to_80_percent < 30)
                }
                
                # Add to network alerts if needed
                if forecast_summary['device_forecasts'][device_id]['capacity_alert']:
                    forecast_summary['network_alerts'].append({
                        "device": device_id,
                        "alert_type": "capacity_warning",
                        "message": f"Device approaching capacity limits: {recent_avg:.1f}% current usage"
                    })
            
            return forecast_summary
            
        except Exception as e:
            # Error handling: Unexpected processing errors
            return {
                "mcp_resource": "network://capacity-forecast",
                "error": f"Forecast processing failed: {str(e)}",
                "error_type": "processing_error",
                "fallback": "Use simplified capacity estimation",
                "debug_info": f"Error occurred during device data processing"
            }
    
    # ===============================
    # MCP TOOLS - Predictive Analysis
    # ===============================
    
    async def tool_predict_device_performance(self, device_id, prediction_hours=24):
        """
        MCP Tool: predict_device_performance
        
        Demonstrates:
        - Input validation for time-series tools
        - AI integration with statistical preprocessing
        - Structured prediction output
        """
        print(f"MCP Tool Called: predict_device_performance(device_id='{device_id}', hours={prediction_hours})")
        
        # Input validation
        if not device_id:
            return {
                "mcp_tool": "predict_device_performance",
                "error": "device_id parameter is required",
                "valid_parameters": {
                    "device_id": "string (required)",
                    "prediction_hours": "integer (1-72, default 24)"
                }
            }
        
        if not isinstance(prediction_hours, int) or prediction_hours < 1 or prediction_hours > 72:
            return {
                "mcp_tool": "predict_device_performance",
                "error": f"prediction_hours must be integer between 1-72, got: {prediction_hours}",
                "default_used": 24
            }
        
        # Load and validate data
        time_series_data = self.load_time_series_data()
        if not time_series_data or device_id not in time_series_data:
            available_devices = [d for d in (time_series_data.keys() if time_series_data else []) if d != 'metadata']
            return {
                "mcp_tool": "predict_device_performance",
                "error": f"Device {device_id} not found in historical data",
                "available_devices": available_devices,
                "suggestion": "Check device_id or use available devices list"
            }
        
        device_data = time_series_data[device_id]
        bw_data = device_data['bandwidth_utilization']
        
        # Prepare statistical context for AI
        recent_avg = sum(bw_data[-24:]) / 24 if len(bw_data) >= 24 else sum(bw_data) / len(bw_data)
        daily_pattern = []
        
        # Extract daily pattern (if enough data)
        if len(bw_data) >= 24:
            for hour in range(24):
                hour_values = [bw_data[i] for i in range(hour, len(bw_data), 24) if i < len(bw_data)]
                if hour_values:
                    daily_pattern.append(f"Hour {hour:02d}: avg {sum(hour_values)/len(hour_values):.1f}%")
        
        # AI prediction with statistical context
        prompt = f"""You are a network performance forecasting specialist.

Device: {device_id}
Prediction Timeframe: Next {prediction_hours} hours
Historical Data Points: {len(bw_data)}
Recent Average Utilization: {recent_avg:.1f}%

Recent Performance Pattern (last 12 hours):
{bw_data[-12:]}

Daily Usage Patterns:
{chr(10).join(daily_pattern[:12]) if daily_pattern else "Insufficient data for daily pattern analysis"}

Provide performance prediction:
1. HOUR-BY-HOUR FORECAST for next {min(prediction_hours, 12)} hours
2. EXPECTED PEAK USAGE periods and values  
3. PREDICTED PERFORMANCE ISSUES or bottlenecks
4. CONFIDENCE LEVEL in predictions (High/Medium/Low)
5. FACTORS that could affect accuracy
6. RECOMMENDED MONITORING priorities

Format with specific timeframes and expected bandwidth percentages."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.4
            )
            
            return {
                "mcp_tool": "predict_device_performance",
                "device_id": device_id,
                "prediction_hours": prediction_hours,
                "baseline_metrics": {
                    "recent_avg_utilization": round(recent_avg, 1),
                    "data_points_analyzed": len(bw_data),
                    "prediction_confidence": "medium"  # Could be calculated based on data quality
                },
                "ai_prediction": response.choices[0].message.content,
                "generated_at": datetime.now().isoformat(),
                "validity_period": f"{prediction_hours} hours from generation"
            }
            
        except Exception as e:
            return {
                "mcp_tool": "predict_device_performance",
                "error": f"Prediction generation failed: {str(e)}",
                "fallback": "Use trend extrapolation: recent_avg={recent_avg:.1f}%",
                "device_id": device_id
            }
    
    async def tool_capacity_analysis(self, threshold_percent=80):
        """
        MCP Tool: capacity_analysis
        
        Demonstrates:
        - Resource composition: Using multiple data sources
        - Business logic integration: Capacity planning rules
        - Comprehensive error handling
        """
        print(f"MCP Tool Called: capacity_analysis(threshold={threshold_percent}%)")
        
        # Input validation
        if not isinstance(threshold_percent, (int, float)) or threshold_percent < 50 or threshold_percent > 100:
            return {
                "mcp_tool": "capacity_analysis",
                "error": f"threshold_percent must be number between 50-100, got: {threshold_percent}",
                "suggestion": "Common thresholds: 70% (early warning), 80% (standard), 90% (critical)"
            }
        
        time_series_data = self.load_time_series_data()
        if not time_series_data:
            return {
                "mcp_tool": "capacity_analysis",
                "error": "Cannot perform capacity analysis without historical data",
                "fallback": "Use current device metrics for basic capacity assessment"
            }
        
        try:
            # Resource composition: Combine performance trends + capacity forecast
            trends_data = await self.resource_performance_trends()
            forecast_data = await self.resource_capacity_forecast()
            
            analysis_result = {
                "mcp_tool": "capacity_analysis",
                "threshold_analyzed": f"{threshold_percent}%",
                "analysis_timestamp": datetime.now().isoformat(),
                "capacity_summary": {
                    "devices_over_threshold": 0,
                    "devices_approaching_threshold": 0,
                    "immediate_action_required": [],
                    "planned_upgrades_needed": []
                },
                "device_analysis": {}
            }
            
            # Analyze each device
            for device_id in trends_data.get('device_trends', {}):
                device_trend = trends_data['device_trends'][device_id]
                device_forecast = forecast_data.get('device_forecasts', {}).get(device_id, {})
                
                peak_util = device_trend['peak_utilization']
                avg_util = device_trend['average_utilization']
                
                # Capacity status determination
                if peak_util > threshold_percent:
                    analysis_result['capacity_summary']['devices_over_threshold'] += 1
                    action_required = "immediate"
                elif avg_util > (threshold_percent * 0.8):  # 80% of threshold
                    analysis_result['capacity_summary']['devices_approaching_threshold'] += 1
                    action_required = "planned"
                else:
                    action_required = "none"
                
                device_analysis = {
                    "current_status": device_trend['capacity_status'],
                    "peak_utilization": peak_util,
                    "average_utilization": avg_util,
                    "trend_direction": device_trend['trend_direction'],
                    "action_required": action_required,
                    "recommendation": self.generate_capacity_recommendation(
                        device_id, peak_util, avg_util, threshold_percent, action_required
                    )
                }
                
                # Add forecast data if available
                if device_forecast and 'error' not in device_forecast:
                    device_analysis['projected_utilization'] = device_forecast.get('projected_utilization_7d')
                    device_analysis['days_to_threshold'] = device_forecast.get('days_to_80_percent')
                
                analysis_result['device_analysis'][device_id] = device_analysis
                
                # Add to action lists
                if action_required == "immediate":
                    analysis_result['capacity_summary']['immediate_action_required'].append(device_id)
                elif action_required == "planned":
                    analysis_result['capacity_summary']['planned_upgrades_needed'].append(device_id)
            
            return analysis_result
            
        except Exception as e:
            return {
                "mcp_tool": "capacity_analysis",
                "error": f"Capacity analysis failed: {str(e)}",
                "fallback": "Perform manual capacity assessment using current metrics"
            }
    
    def generate_capacity_recommendation(self, device_id, peak_util, avg_util, threshold, action_required):
        """Helper function to generate capacity recommendations"""
        if action_required == "immediate":
            return f"URGENT: {device_id} exceeds {threshold}% threshold ({peak_util}% peak). Schedule immediate capacity upgrade."
        elif action_required == "planned":
            return f"PLANNED: {device_id} approaching limits ({avg_util}% avg). Plan capacity upgrade within 30 days."
        else:
            return f"NORMAL: {device_id} within acceptable limits ({peak_util}% peak). Continue monitoring."

async def main():
    """Demonstrate intermediate MCP concepts for performance prediction"""
    print("AI Network Performance Predictor - MCP Concepts Demo")
    print("=" * 60)
    print("Demonstrates: State Management, Data Handling, Error Patterns, Resource Composition")
    print("=" * 60)
    
    predictor = PerformancePredictorMCPDemo()
    
    # ===============================
    # DEMONSTRATE MCP STATE MANAGEMENT
    # ===============================
    print("\n1. MCP STATE MANAGEMENT (Stateless Time-Series Processing):")
    print("-" * 60)
    
    # Show stateless data loading
    performance_trends = await predictor.resource_performance_trends()
    if "error" in performance_trends:
        print(f"Error: {performance_trends['error']}")
        return
    
    print(f"✅ Resource: {performance_trends['mcp_resource']}")
    print(f"📊 Data Period: {performance_trends['data_period']}")
    print(f"🔄 Fresh Data Load: {performance_trends['analysis_timestamp']}")
    print(f"📈 Devices Analyzed: {performance_trends['network_summary']['total_devices']}")
    
    print("\n📋 Device Performance Trends:")
    for device_id, trend in performance_trends['device_trends'].items():
        status_icon = {"normal": "✅", "warning": "⚠️", "critical": "🔴"}
        icon = status_icon[trend['capacity_status']]
        print(f"  {icon} {device_id}: {trend['average_utilization']}% avg, {trend['peak_utilization']}% peak, {trend['trend_direction']} trend")
    
    # ===============================
    # DEMONSTRATE ERROR HANDLING PATTERNS
    # ===============================
    print(f"\n\n2. MCP ERROR HANDLING PATTERNS:")
    print("-" * 40)
    
    # Test with invalid device
    invalid_result = await predictor.tool_predict_device_performance("invalid-device")
    # Test with invalid device
    invalid_result = await predictor.tool_predict_device_performance("invalid-device")
    print(f"🔧 Tool: {invalid_result['mcp_tool']}")
    print(f"❌ Error Handling: {invalid_result['error']}")
    print(f"💡 Available Devices: {invalid_result['available_devices']}")
    
    # Test with invalid parameters
    invalid_params = await predictor.tool_predict_device_performance("router-01", 100)  # Invalid hours
    print(f"❌ Parameter Validation: {invalid_params['error']}")
    
    # ===============================
    # DEMONSTRATE DATA HANDLING
    # ===============================
    print(f"\n\n3. MCP DATA HANDLING (Efficient Time-Series Processing):")
    print("-" * 55)
    
    # Test capacity forecast with data size considerations
    capacity_forecast = await predictor.resource_capacity_forecast()
    print(f"✅ Resource: {capacity_forecast['mcp_resource']}")
    print(f"📅 Forecast Horizon: {capacity_forecast['forecast_horizon']}")
    
    if capacity_forecast.get('network_alerts'):
        print(f"⚠️ Network Alerts: {len(capacity_forecast['network_alerts'])} devices need attention")
        for alert in capacity_forecast['network_alerts']:
            print(f"   - {alert['device']}: {alert['message']}")
    else:
        print("✅ No capacity alerts detected")
    
    # ===============================
    # DEMONSTRATE RESOURCE COMPOSITION
    # ===============================
    print(f"\n\n4. MCP RESOURCE COMPOSITION (Combining Multiple Data Sources):")
    print("-" * 65)
    
    # Test comprehensive capacity analysis (uses multiple resources)
    capacity_analysis = await predictor.tool_capacity_analysis(75)  # 75% threshold
    print(f"🔧 Tool: {capacity_analysis['mcp_tool']}")
    print(f"📊 Threshold: {capacity_analysis['threshold_analyzed']}")
    
    summary = capacity_analysis['capacity_summary']
    print(f"📈 Analysis Summary:")
    print(f"   - Devices over threshold: {summary['devices_over_threshold']}")
    print(f"   - Devices approaching threshold: {summary['devices_approaching_threshold']}")
    
    if summary['immediate_action_required']:
        print(f"🔴 Immediate Action Required: {', '.join(summary['immediate_action_required'])}")
    
    if summary['planned_upgrades_needed']:
        print(f"🟡 Planned Upgrades Needed: {', '.join(summary['planned_upgrades_needed'])}")
    
    # ===============================
    # DEMONSTRATE SUCCESSFUL PREDICTION
    # ===============================
    print(f"\n\n5. MCP TOOLS (Successful AI Prediction):")
    print("-" * 40)
    
    # Test successful device prediction
    prediction_result = await predictor.tool_predict_device_performance("router-01", 12)
    if "error" not in prediction_result:
        print(f"🔧 Tool: {prediction_result['mcp_tool']}")
        print(f"🎯 Device: {prediction_result['device_id']}")
        print(f"⏱️ Prediction Window: {prediction_result['prediction_hours']} hours")
        print(f"📊 Baseline: {prediction_result['baseline_metrics']['recent_avg_utilization']}% recent average")
        
        print(f"\n🧠 AI Performance Prediction:")
        prediction_text = prediction_result['ai_prediction']
        print(prediction_text[:500] + "..." if len(prediction_text) > 500 else prediction_text)
    
    # ===============================
    # MCP CONCEPTS SUMMARY
    # ===============================
    print(f"\n{'='*60}")
    print("🎓 INTERMEDIATE MCP CONCEPTS DEMONSTRATED:")
    print("=" * 60)
    print("✅ State Management: Stateless time-series processing with fresh data loading")
    print("✅ Data Handling: Efficient processing of large historical datasets")
    print("✅ Error Patterns: Comprehensive error handling for data processing failures")
    print("✅ Resource Composition: Combining performance trends + capacity forecasts")
    print("✅ Input Validation: Parameter checking for time-series analysis tools")
    print("✅ Data Size Considerations: Summarized metrics vs raw time-series data")
    print("✅ Business Logic Integration: Capacity planning rules and thresholds")
    print("\n💡 This shows how to build robust, scalable MCP servers for")
    print("   time-series analysis and predictive network operations!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())