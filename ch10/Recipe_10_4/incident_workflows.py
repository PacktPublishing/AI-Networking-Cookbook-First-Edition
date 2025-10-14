#!/usr/bin/env python3
"""
Incident-Specific Response Workflows
Defines specialized response procedures for different types of security incidents.
"""

import json
import logging
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    step_id: str
    name: str
    description: str
    action_type: str
    parameters: Dict[str, Any]
    prerequisites: List[str] = None
    timeout_minutes: int = 10
    critical: bool = False
    status: WorkflowStatus = WorkflowStatus.PENDING
    execution_time: Optional[datetime.datetime] = None
    result: Optional[str] = None

class RansomwareWorkflow:
    """Specialized workflow for ransomware incidents"""
    
    @staticmethod
    def generate_workflow(incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Generate ransomware response workflow"""
        affected_systems = incident_data.get('affected_systems', [])
        c2_ips = incident_data.get('indicators', {}).get('c2_ips', [])
        
        steps = []
        
        # Immediate containment phase
        steps.extend([
            WorkflowStep(
                step_id="RANSOM_001",
                name="Emergency Network Isolation",
                description="Immediately isolate all affected systems from network",
                action_type="isolate_systems",
                parameters={
                    "systems": affected_systems,
                    "method": "emergency_isolation",
                    "preserve_evidence": True
                },
                timeout_minutes=2,
                critical=True
            ),
            WorkflowStep(
                step_id="RANSOM_002", 
                name="Block C2 Communications",
                description="Block command and control server IPs",
                action_type="block_ips",
                parameters={
                    "ip_list": c2_ips,
                    "rule_type": "emergency_block",
                    "apply_to_all_firewalls": True
                },
                timeout_minutes=5,
                critical=True
            ),
            WorkflowStep(
                step_id="RANSOM_003",
                name="Disable File Shares",
                description="Temporarily disable network file shares to prevent spread",
                action_type="disable_services",
                parameters={
                    "services": ["SMB", "NFS", "FTP"],
                    "scope": "organization_wide"
                },
                timeout_minutes=5,
                critical=True
            )
        ])
        
        # Investigation phase
        steps.extend([
            WorkflowStep(
                step_id="RANSOM_004",
                name="Collect Memory Dumps",
                description="Collect memory dumps from infected systems",
                action_type="collect_evidence",
                parameters={
                    "systems": affected_systems,
                    "evidence_type": "memory_dump",
                    "encryption": True
                },
                prerequisites=["RANSOM_001"],
                timeout_minutes=30
            ),
            WorkflowStep(
                step_id="RANSOM_005",
                name="Identify Ransomware Variant",
                description="Analyze samples to identify ransomware family",
                action_type="malware_analysis",
                parameters={
                    "sample_locations": "/evidence/samples/",
                    "analysis_type": "automated",
                    "sandbox_analysis": True
                },
                prerequisites=["RANSOM_004"],
                timeout_minutes=20
            ),
            WorkflowStep(
                step_id="RANSOM_006",
                name="Check for Decryption Tools",
                description="Search for available decryption tools",
                action_type="decryption_research",
                parameters={
                    "ransomware_family": "TBD",
                    "check_nomoreransom": True,
                    "check_vendor_tools": True
                },
                prerequisites=["RANSOM_005"],
                timeout_minutes=15
            )
        ])
        
        # Recovery phase
        steps.extend([
            WorkflowStep(
                step_id="RANSOM_007",
                name="Assess Backup Integrity",
                description="Verify backup systems are not compromised",
                action_type="backup_verification",
                parameters={
                    "backup_systems": ["primary_backup", "offsite_backup"],
                    "integrity_check": True,
                    "malware_scan": True
                },
                timeout_minutes=45
            ),
            WorkflowStep(
                step_id="RANSOM_008",
                name="Begin System Restoration",
                description="Start restoring systems from clean backups",
                action_type="system_restore",
                parameters={
                    "restore_priority": ["critical_servers", "user_workstations"],
                    "verification_required": True
                },
                prerequisites=["RANSOM_007"],
                timeout_minutes=120
            )
        ])
        
        return steps

class DataExfiltrationWorkflow:
    """Specialized workflow for data exfiltration incidents"""
    
    @staticmethod
    def generate_workflow(incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Generate data exfiltration response workflow"""
        affected_systems = incident_data.get('affected_systems', [])
        external_ips = incident_data.get('indicators', {}).get('external_ips', [])
        user_account = incident_data.get('indicators', {}).get('user_account')
        
        steps = []
        
        # Immediate response
        steps.extend([
            WorkflowStep(
                step_id="EXFIL_001",
                name="Block External Destinations",
                description="Block communication to external exfiltration destinations",
                action_type="block_ips",
                parameters={
                    "ip_list": external_ips,
                    "rule_type": "exfiltration_block",
                    "log_attempts": True
                },
                timeout_minutes=3,
                critical=True
            ),
            WorkflowStep(
                step_id="EXFIL_002",
                name="Isolate Source Systems",
                description="Isolate systems involved in data exfiltration",
                action_type="isolate_systems",
                parameters={
                    "systems": affected_systems,
                    "method": "network_isolation",
                    "maintain_monitoring": True
                },
                timeout_minutes=5,
                critical=True
            )
        ])
        
        # Account security
        if user_account:
            steps.append(
                WorkflowStep(
                    step_id="EXFIL_003",
                    name="Secure Compromised Account",
                    description="Disable compromised user account and reset credentials",
                    action_type="account_security",
                    parameters={
                        "account": user_account,
                        "actions": ["disable", "reset_password", "revoke_tokens"],
                        "force_logout": True
                    },
                    timeout_minutes=5,
                    critical=True
                )
            )
        
        # Investigation
        steps.extend([
            WorkflowStep(
                step_id="EXFIL_004",
                name="Analyze Data Access Patterns",
                description="Review file access logs to determine scope of compromise",
                action_type="log_analysis",
                parameters={
                    "log_sources": ["file_server", "database", "sharepoint"],
                    "time_range_hours": 48,
                    "focus_user": user_account
                },
                timeout_minutes=30
            ),
            WorkflowStep(
                step_id="EXFIL_005",
                name="Identify Exfiltrated Data",
                description="Determine what data was potentially exfiltrated",
                action_type="data_classification",
                parameters={
                    "source_directories": incident_data.get('indicators', {}).get('source_directories', []),
                    "classification_scan": True,
                    "privacy_assessment": True
                },
                prerequisites=["EXFIL_004"],
                timeout_minutes=45
            ),
            WorkflowStep(
                step_id="EXFIL_006",
                name="Network Traffic Analysis",
                description="Analyze network traffic for exfiltration patterns",
                action_type="network_analysis",
                parameters={
                    "capture_period_hours": 24,
                    "analyze_protocols": ["HTTPS", "FTP", "SFTP", "DNS"],
                    "external_destinations": external_ips
                },
                timeout_minutes=60
            )
        ])
        
        # Compliance and notification
        compliance_reqs = incident_data.get('impact_assessment', {}).get('compliance_implications', [])
        if compliance_reqs:
            steps.append(
                WorkflowStep(
                    step_id="EXFIL_007",
                    name="Compliance Notification",
                    description="Notify relevant authorities per compliance requirements",
                    action_type="compliance_notification",
                    parameters={
                        "regulations": compliance_reqs,
                        "notification_window_hours": 72,
                        "include_data_assessment": True
                    },
                    prerequisites=["EXFIL_005"],
                    timeout_minutes=30,
                    critical=True
                )
            )
        
        return steps

class CredentialCompromiseWorkflow:
    """Specialized workflow for credential compromise incidents"""
    
    @staticmethod
    def generate_workflow(incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Generate credential compromise response workflow"""
        compromised_accounts = incident_data.get('indicators', {}).get('compromised_accounts', [])
        source_ip = incident_data.get('indicators', {}).get('source_ip')
        affected_systems = incident_data.get('affected_systems', [])
        
        steps = []
        
        # Immediate containment
        steps.extend([
            WorkflowStep(
                step_id="CRED_001",
                name="Disable Compromised Accounts",
                description="Immediately disable all compromised user accounts",
                action_type="disable_accounts",
                parameters={
                    "accounts": compromised_accounts,
                    "revoke_sessions": True,
                    "revoke_tokens": True
                },
                timeout_minutes=5,
                critical=True
            ),
            WorkflowStep(
                step_id="CRED_002",
                name="Block Attack Source",
                description="Block the source IP of the credential attack",
                action_type="block_ips",
                parameters={
                    "ip_list": [source_ip] if source_ip else [],
                    "rule_type": "credential_attack_block",
                    "duration_hours": 24
                },
                timeout_minutes=3,
                critical=True
            )
        ])
        
        # Security assessment
        steps.extend([
            WorkflowStep(
                step_id="CRED_003",
                name="Assess Privilege Escalation",
                description="Check for unauthorized privilege escalations",
                action_type="privilege_audit",
                parameters={
                    "accounts": compromised_accounts,
                    "check_group_memberships": True,
                    "check_permissions": True,
                    "compare_baseline": True
                },
                timeout_minutes=20
            ),
            WorkflowStep(
                step_id="CRED_004",
                name="Review Authentication Logs",
                description="Analyze authentication logs for attack patterns",
                action_type="log_analysis",
                parameters={
                    "log_sources": ["domain_controller", "vpn", "web_applications"],
                    "time_range_hours": 72,
                    "failed_login_threshold": 10
                },
                timeout_minutes=30
            ),
            WorkflowStep(
                step_id="CRED_005",
                name="Lateral Movement Detection",
                description="Check for signs of lateral movement",
                action_type="lateral_movement_analysis",
                parameters={
                    "source_systems": affected_systems,
                    "check_rdp_sessions": True,
                    "check_smb_access": True,
                    "check_powershell_activity": True
                },
                prerequisites=["CRED_004"],
                timeout_minutes=45
            )
        ])
        
        # Recovery actions
        steps.extend([
            WorkflowStep(
                step_id="CRED_006",
                name="Force Password Reset",
                description="Force password reset for all potentially affected accounts",
                action_type="password_reset",
                parameters={
                    "scope": "organization_wide" if len(compromised_accounts) > 5 else "targeted",
                    "require_mfa_setup": True,
                    "minimum_complexity": "high"
                },
                prerequisites=["CRED_003"],
                timeout_minutes=60
            ),
            WorkflowStep(
                step_id="CRED_007",
                name="Rebuild Compromised Systems",
                description="Rebuild systems with administrative access",
                action_type="system_rebuild",
                parameters={
                    "systems": affected_systems,
                    "backup_data": True,
                    "security_hardening": True
                },
                prerequisites=["CRED_005"],
                timeout_minutes=180
            )
        ])
        
        return steps

class DDoSWorkflow:
    """Specialized workflow for DDoS attack incidents"""
    
    @staticmethod
    def generate_workflow(incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Generate DDoS response workflow"""
        attack_sources = incident_data.get('indicators', {}).get('attack_sources', [])
        affected_systems = incident_data.get('affected_systems', [])
        attack_types = incident_data.get('indicators', {}).get('attack_types', [])
        
        steps = []
        
        # Immediate mitigation
        steps.extend([
            WorkflowStep(
                step_id="DDOS_001",
                name="Activate DDoS Protection",
                description="Enable DDoS protection services",
                action_type="ddos_protection",
                parameters={
                    "protection_level": "maximum",
                    "scrubbing_centers": True,
                    "rate_limiting": True
                },
                timeout_minutes=5,
                critical=True
            ),
            WorkflowStep(
                step_id="DDOS_002",
                name="Block Attack Sources",
                description="Block identified attack source networks",
                action_type="block_networks",
                parameters={
                    "networks": attack_sources,
                    "rule_type": "ddos_block",
                    "upstream_filtering": True
                },
                timeout_minutes=10,
                critical=True
            )
        ])
        
        # Traffic analysis and filtering
        steps.extend([
            WorkflowStep(
                step_id="DDOS_003",
                name="Analyze Attack Patterns",
                description="Analyze traffic patterns to identify attack vectors",
                action_type="traffic_analysis",
                parameters={
                    "attack_types": attack_types,
                    "pattern_recognition": True,
                    "geolocation_analysis": True
                },
                timeout_minutes=15
            ),
            WorkflowStep(
                step_id="DDOS_004",
                name="Implement Filtering Rules",
                description="Create specific filtering rules based on attack patterns",
                action_type="traffic_filtering",
                parameters={
                    "filter_types": ["packet_size", "request_rate", "geographic"],
                    "whitelist_known_good": True,
                    "adaptive_filtering": True
                },
                prerequisites=["DDOS_003"],
                timeout_minutes=20
            )
        ])
        
        # Service restoration
        steps.extend([
            WorkflowStep(
                step_id="DDOS_005",
                name="Scale Infrastructure",
                description="Scale up infrastructure to handle attack volume",
                action_type="infrastructure_scaling",
                parameters={
                    "auto_scaling": True,
                    "load_balancing": True,
                    "cdn_activation": True
                },
                timeout_minutes=30
            ),
            WorkflowStep(
                step_id="DDOS_006",
                name="Monitor Service Availability",
                description="Continuously monitor service availability and performance",
                action_type="availability_monitoring",
                parameters={
                    "check_interval_seconds": 30,
                    "performance_thresholds": {"response_time": 2000, "success_rate": 95},
                    "alert_degradation": True
                },
                timeout_minutes=60
            )
        ])
        
        return steps

class InsiderThreatWorkflow:
    """Specialized workflow for insider threat incidents"""
    
    @staticmethod
    def generate_workflow(incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Generate insider threat response workflow"""
        employee_id = incident_data.get('indicators', {}).get('employee_id')
        accessed_systems = incident_data.get('indicators', {}).get('accessed_systems', [])
        data_accessed = incident_data.get('indicators', {}).get('data_accessed', [])
        
        steps = []
        
        # Discrete monitoring
        steps.extend([
            WorkflowStep(
                step_id="INSIDER_001",
                name="Enable Enhanced Monitoring",
                description="Enable detailed monitoring of user activities",
                action_type="user_monitoring",
                parameters={
                    "employee_id": employee_id,
                    "monitor_file_access": True,
                    "monitor_network_activity": True,
                    "monitor_email": True,
                    "discrete_mode": True
                },
                timeout_minutes=10,
                critical=True
            ),
            WorkflowStep(
                step_id="INSIDER_002",
                name="Review Access Permissions",
                description="Review user's current access permissions",
                action_type="permission_audit",
                parameters={
                    "employee_id": employee_id,
                    "systems": accessed_systems,
                    "check_job_role_alignment": True,
                    "historical_access_review": True
                },
                timeout_minutes=20
            )
        ])
        
        # Investigation
        steps.extend([
            WorkflowStep(
                step_id="INSIDER_003",
                name="Analyze User Behavior",
                description="Analyze user behavior patterns for anomalies",
                action_type="behavior_analysis",
                parameters={
                    "employee_id": employee_id,
                    "time_range_days": 30,
                    "compare_peer_group": True,
                    "anomaly_detection": True
                },
                timeout_minutes=45
            ),
            WorkflowStep(
                step_id="INSIDER_004",
                name="Data Loss Assessment",
                description="Assess potential data loss or misuse",
                action_type="data_loss_assessment",
                parameters={
                    "data_types": data_accessed,
                    "export_detection": True,
                    "external_communication_check": True
                },
                prerequisites=["INSIDER_003"],
                timeout_minutes=30
            )
        ])
        
        # Coordinated response
        steps.extend([
            WorkflowStep(
                step_id="INSIDER_005",
                name="HR Coordination",
                description="Coordinate with HR for personnel action",
                action_type="hr_coordination",
                parameters={
                    "employee_id": employee_id,
                    "recommended_actions": ["investigation", "access_review"],
                    "evidence_package": True
                },
                prerequisites=["INSIDER_004"],
                timeout_minutes=60
            ),
            WorkflowStep(
                step_id="INSIDER_006",
                name="Legal Review",
                description="Initiate legal review of incident",
                action_type="legal_review",
                parameters={
                    "incident_type": "insider_threat",
                    "evidence_preservation": True,
                    "potential_violations": ["data_access_policy", "confidentiality_agreement"]
                },
                prerequisites=["INSIDER_005"],
                timeout_minutes=120
            )
        ])
        
        return steps

class WorkflowEngine:
    """Engine for executing incident-specific workflows"""
    
    def __init__(self):
        self.active_workflows = {}
        self.workflow_generators = {
            "malware_outbreak": RansomwareWorkflow.generate_workflow,
            "data_exfiltration": DataExfiltrationWorkflow.generate_workflow,
            "credential_compromise": CredentialCompromiseWorkflow.generate_workflow,
            "ddos_attack": DDoSWorkflow.generate_workflow,
            "insider_threat": InsiderThreatWorkflow.generate_workflow
        }
        
    def create_workflow(self, incident_id: str, incident_type: str, incident_data: Dict[str, Any]) -> List[WorkflowStep]:
        """Create workflow for specific incident type"""
        if incident_type not in self.workflow_generators:
            raise ValueError(f"No workflow defined for incident type: {incident_type}")
            
        workflow_steps = self.workflow_generators[incident_type](incident_data)
        self.active_workflows[incident_id] = workflow_steps
        
        logging.info(f"Created workflow for incident {incident_id} with {len(workflow_steps)} steps")
        return workflow_steps
        
    def get_workflow_status(self, incident_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        if incident_id not in self.active_workflows:
            return {"error": "Workflow not found"}
            
        workflow = self.active_workflows[incident_id]
        
        status_summary = {
            "total_steps": len(workflow),
            "completed": len([s for s in workflow if s.status == WorkflowStatus.COMPLETED]),
            "failed": len([s for s in workflow if s.status == WorkflowStatus.FAILED]),
            "in_progress": len([s for s in workflow if s.status == WorkflowStatus.IN_PROGRESS]),
            "pending": len([s for s in workflow if s.status == WorkflowStatus.PENDING]),
            "steps": []
        }
        
        for step in workflow:
            status_summary["steps"].append({
                "step_id": step.step_id,
                "name": step.name,
                "status": step.status.value,
                "critical": step.critical,
                "execution_time": step.execution_time.isoformat() if step.execution_time else None,
                "result": step.result
            })
            
        return status_summary
        
    def get_next_steps(self, incident_id: str) -> List[WorkflowStep]:
        """Get next executable steps in workflow"""
        if incident_id not in self.active_workflows:
            return []
            
        workflow = self.active_workflows[incident_id]
        next_steps = []
        
        for step in workflow:
            if step.status != WorkflowStatus.PENDING:
                continue
                
            # Check prerequisites
            if step.prerequisites:
                prereq_met = True
                for prereq_id in step.prerequisites:
                    prereq_step = next((s for s in workflow if s.step_id == prereq_id), None)
                    if not prereq_step or prereq_step.status != WorkflowStatus.COMPLETED:
                        prereq_met = False
                        break
                        
                if not prereq_met:
                    continue
                    
            next_steps.append(step)
            
        return next_steps
        
    def update_step_status(self, incident_id: str, step_id: str, status: WorkflowStatus, result: str = None):
        """Update status of workflow step"""
        if incident_id not in self.active_workflows:
            return False
            
        workflow = self.active_workflows[incident_id]
        step = next((s for s in workflow if s.step_id == step_id), None)
        
        if step:
            step.status = status
            step.result = result
            if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                step.execution_time = datetime.datetime.now()
            return True
            
        return False

def main():
    """Test workflow generation"""
    
    # Test ransomware workflow
    ransomware_data = {
        "affected_systems": ["10.0.1.150", "10.0.1.175"],
        "indicators": {
            "c2_ips": ["198.51.100.25", "203.0.113.50"],
            "encrypted_file_extensions": [".locked", ".encrypted"]
        }
    }
    
    engine = WorkflowEngine()
    workflow = engine.create_workflow("INC-001", "malware_outbreak", ransomware_data)
    
    print(f"Generated ransomware workflow with {len(workflow)} steps:")
    for step in workflow:
        print(f"  {step.step_id}: {step.name} ({'CRITICAL' if step.critical else 'Normal'})")
        
    # Test getting next steps
    next_steps = engine.get_next_steps("INC-001")
    print(f"\nNext executable steps: {len(next_steps)}")
    for step in next_steps:
        print(f"  {step.step_id}: {step.name}")

if __name__ == "__main__":
    main()