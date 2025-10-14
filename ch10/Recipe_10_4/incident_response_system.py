#!/usr/bin/env python3
"""
Automated Incident Response System
A defensive security tool for isolating infected systems, blocking malicious IPs, 
and collecting forensic evidence during security incidents.
"""

import json
import yaml
import logging
import datetime
import hashlib
import subprocess
import os
import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import requests
import paramiko
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    RANSOMWARE = "malware_outbreak"
    DATA_EXFILTRATION = "data_exfiltration"
    CREDENTIAL_COMPROMISE = "credential_compromise"
    INSIDER_THREAT = "insider_threat"
    DDOS_ATTACK = "ddos_attack"
    SUPPLY_CHAIN = "supply_chain_compromise"

class ResponseAction(Enum):
    ISOLATE_SYSTEM = "isolate_system"
    BLOCK_IP = "block_ip"
    COLLECT_EVIDENCE = "collect_evidence"
    DISABLE_ACCOUNT = "disable_account"
    QUARANTINE_FILE = "quarantine_file"
    NOTIFY_STAKEHOLDERS = "notify_stakeholders"

@dataclass
class IncidentData:
    incident_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    detection_time: datetime.datetime
    affected_systems: List[str]
    indicators: Dict[str, Any]
    description: str
    status: str = "active"

@dataclass
class ResponseStep:
    action: ResponseAction
    target: str
    parameters: Dict[str, Any]
    status: str = "pending"
    execution_time: Optional[datetime.datetime] = None
    result: Optional[str] = None

class NetworkDevice:
    def __init__(self, name: str, ip: str, device_type: str, management_protocol: str = "ssh"):
        self.name = name
        self.ip = ip
        self.device_type = device_type
        self.management_protocol = management_protocol
        
    def execute_command(self, command: str, username: str, password: str) -> str:
        """Execute command on network device via SSH"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=username, password=password, timeout=30)
            
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode()
            error = stderr.read().decode()
            
            ssh.close()
            
            if error:
                raise Exception(f"Command failed: {error}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to execute command on {self.name}: {str(e)}")
            raise

class FirewallManager:
    def __init__(self, devices: List[NetworkDevice]):
        self.devices = devices
        
    def block_ip_address(self, ip_address: str, rule_name: str = None) -> bool:
        """Block IP address on all firewall devices"""
        success_count = 0
        
        for device in self.devices:
            try:
                if "palo_alto" in device.device_type.lower():
                    command = f"configure\nset rulebase security rules BLOCK_{ip_address.replace('.', '_')} from any to any source {ip_address} action deny\ncommit"
                elif "cisco" in device.device_type.lower():
                    command = f"configure terminal\naccess-list 100 deny ip host {ip_address} any\nexit\nwrite memory"
                else:
                    logging.warning(f"Unknown firewall type: {device.device_type}")
                    continue
                    
                result = device.execute_command(command, "admin", "password")
                logging.info(f"Successfully blocked {ip_address} on {device.name}")
                success_count += 1
                
            except Exception as e:
                logging.error(f"Failed to block IP {ip_address} on {device.name}: {str(e)}")
                
        return success_count > 0

class SwitchManager:
    def __init__(self, devices: List[NetworkDevice]):
        self.devices = devices
        
    def isolate_port_by_ip(self, target_ip: str) -> bool:
        """Isolate network port based on IP address"""
        for device in self.devices:
            try:
                # Get ARP table to find port
                arp_command = "show ip arp"
                arp_result = device.execute_command(arp_command, "admin", "password")
                
                # Find MAC address for IP
                mac_address = self._extract_mac_from_arp(arp_result, target_ip)
                if not mac_address:
                    continue
                    
                # Get CAM table to find port
                cam_command = f"show mac address-table address {mac_address}"
                cam_result = device.execute_command(cam_command, "admin", "password")
                
                port = self._extract_port_from_cam(cam_result)
                if port:
                    shutdown_command = f"configure terminal\ninterface {port}\nshutdown\nexit\nwrite memory"
                    device.execute_command(shutdown_command, "admin", "password")
                    logging.info(f"Successfully isolated port {port} for IP {target_ip} on {device.name}")
                    return True
                    
            except Exception as e:
                logging.error(f"Failed to isolate IP {target_ip} on {device.name}: {str(e)}")
                
        return False
        
    def _extract_mac_from_arp(self, arp_output: str, target_ip: str) -> Optional[str]:
        """Extract MAC address from ARP table output"""
        for line in arp_output.split('\n'):
            if target_ip in line:
                parts = line.split()
                for part in parts:
                    if ':' in part and len(part) == 17:
                        return part
        return None
        
    def _extract_port_from_cam(self, cam_output: str) -> Optional[str]:
        """Extract port from CAM table output"""
        for line in cam_output.split('\n'):
            if 'Gi' in line or 'Fa' in line or 'Eth' in line:
                parts = line.split()
                for part in parts:
                    if any(x in part for x in ['Gi', 'Fa', 'Eth']):
                        return part
        return None

class EDRManager:
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
    def isolate_endpoint(self, host_ip: str) -> bool:
        """Isolate endpoint using EDR system"""
        try:
            # Get host ID from IP
            host_search_url = f"{self.api_endpoint}/devices/queries/devices/v1"
            params = {'filter': f"local_ip:'{host_ip}'"}
            
            response = requests.get(host_search_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            host_data = response.json()
            if not host_data.get('resources'):
                logging.error(f"No host found with IP {host_ip}")
                return False
                
            host_id = host_data['resources'][0]
            
            # Isolate the host
            isolate_url = f"{self.api_endpoint}/devices/entities/devices-actions/v2"
            isolation_data = {
                'ids': [host_id],
                'action_name': 'contain'
            }
            
            response = requests.post(isolate_url, headers=self.headers, json=isolation_data)
            response.raise_for_status()
            
            logging.info(f"Successfully isolated endpoint {host_ip} (ID: {host_id})")
            return True
            
        except Exception as e:
            logging.error(f"Failed to isolate endpoint {host_ip}: {str(e)}")
            return False

class ForensicsCollector:
    def __init__(self, evidence_directory: str):
        self.evidence_directory = evidence_directory
        os.makedirs(evidence_directory, exist_ok=True)
        
    def collect_memory_dump(self, target_ip: str, incident_id: str) -> Optional[str]:
        """Collect memory dump from target system"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dump_filename = f"{incident_id}_{target_ip}_{timestamp}_memory.dump"
            dump_path = os.path.join(self.evidence_directory, dump_filename)
            
            # This would integrate with tools like WinPmem, LiME, etc.
            logging.info(f"Memory dump collection initiated for {target_ip}")
            logging.info(f"Dump will be saved to: {dump_path}")
            
            return dump_path
            
        except Exception as e:
            logging.error(f"Failed to collect memory dump from {target_ip}: {str(e)}")
            return None
            
    def collect_disk_image(self, target_ip: str, incident_id: str) -> Optional[str]:
        """Collect disk image from target system"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{incident_id}_{target_ip}_{timestamp}_disk.img"
            image_path = os.path.join(self.evidence_directory, image_filename)
            
            logging.info(f"Disk imaging initiated for {target_ip}")
            logging.info(f"Image will be saved to: {image_path}")
            
            return image_path
            
        except Exception as e:
            logging.error(f"Failed to collect disk image from {target_ip}: {str(e)}")
            return None
            
    def collect_network_logs(self, incident_id: str, time_range: int = 24) -> Optional[str]:
        """Collect network logs for specified time range"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"{incident_id}_{timestamp}_network_logs.json"
            log_path = os.path.join(self.evidence_directory, log_filename)
            
            # This would integrate with SIEM, firewall logs, etc.
            logging.info(f"Network log collection initiated for past {time_range} hours")
            logging.info(f"Logs will be saved to: {log_path}")
            
            return log_path
            
        except Exception as e:
            logging.error(f"Failed to collect network logs: {str(e)}")
            return None

class IncidentClassifier:
    def __init__(self, scenarios_file: str):
        with open(scenarios_file, 'r') as f:
            self.scenarios = json.load(f)
            
    def classify_incident(self, incident_data: Dict[str, Any]) -> IncidentData:
        """Classify incident based on indicators and patterns"""
        incident_type = self._determine_incident_type(incident_data)
        severity = self._determine_severity(incident_data)
        
        return IncidentData(
            incident_id=self._generate_incident_id(),
            incident_type=incident_type,
            severity=severity,
            detection_time=datetime.datetime.now(),
            affected_systems=incident_data.get('affected_systems', []),
            indicators=incident_data.get('indicators', {}),
            description=incident_data.get('description', '')
        )
        
    def _determine_incident_type(self, data: Dict[str, Any]) -> IncidentType:
        """Determine incident type based on indicators"""
        indicators = data.get('indicators', {})
        
        if any(ext in str(indicators) for ext in ['.locked', '.encrypted', '.crypto']):
            return IncidentType.RANSOMWARE
        elif 'data_volume' in indicators or 'external_ips' in indicators:
            return IncidentType.DATA_EXFILTRATION
        elif 'compromised_accounts' in indicators or 'privilege_escalation' in indicators:
            return IncidentType.CREDENTIAL_COMPROMISE
        elif 'attack_volume' in indicators or 'attack_sources' in indicators:
            return IncidentType.DDOS_ATTACK
        elif 'compromised_software' in indicators or 'vendor' in indicators:
            return IncidentType.SUPPLY_CHAIN
        else:
            return IncidentType.INSIDER_THREAT
            
    def _determine_severity(self, data: Dict[str, Any]) -> IncidentSeverity:
        """Determine incident severity based on impact"""
        severity_str = data.get('severity', 'medium').lower()
        
        severity_map = {
            'low': IncidentSeverity.LOW,
            'medium': IncidentSeverity.MEDIUM,
            'high': IncidentSeverity.HIGH,
            'critical': IncidentSeverity.CRITICAL
        }
        
        return severity_map.get(severity_str, IncidentSeverity.MEDIUM)
        
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INC-{timestamp}"

class IncidentResponseEngine:
    def __init__(self, config_file: str):
        self.config = self._load_config(config_file)
        self.db_path = "incident_response.db"
        self._init_database()
        
        # Initialize managers
        self.firewall_manager = self._init_firewall_manager()
        self.switch_manager = self._init_switch_manager()
        self.edr_manager = self._init_edr_manager()
        self.forensics_collector = ForensicsCollector("./evidence")
        self.incident_classifier = IncidentClassifier("./mock_data/incident_scenarios.json")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('incident_response.log'),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
            
    def _init_database(self):
        """Initialize SQLite database for incident tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                incident_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                detection_time TEXT NOT NULL,
                affected_systems TEXT,
                indicators TEXT,
                description TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                target TEXT NOT NULL,
                parameters TEXT,
                status TEXT DEFAULT 'pending',
                execution_time TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _init_firewall_manager(self) -> FirewallManager:
        """Initialize firewall manager with devices from config"""
        devices = []
        for fw in self.config.get('network_infrastructure', {}).get('firewalls', []):
            device = NetworkDevice(
                name=fw['name'],
                ip=fw['ip'],
                device_type=fw['type'],
                management_protocol='ssh'
            )
            devices.append(device)
        return FirewallManager(devices)
        
    def _init_switch_manager(self) -> SwitchManager:
        """Initialize switch manager with devices from config"""
        devices = []
        for switch in self.config.get('network_infrastructure', {}).get('switches', []):
            device = NetworkDevice(
                name=switch['name'],
                ip=switch['ip'],
                device_type=switch['type'],
                management_protocol=switch.get('management_protocol', 'ssh')
            )
            devices.append(device)
        return SwitchManager(devices)
        
    def _init_edr_manager(self) -> EDRManager:
        """Initialize EDR manager"""
        edr_config = self.config.get('security_tools', {}).get('edr', [{}])[0]
        return EDRManager(
            api_endpoint=edr_config.get('api_endpoint', ''),
            api_key=os.getenv('EDR_API_KEY', 'demo_key')
        )
        
    def process_incident(self, incident_data: Dict[str, Any]) -> str:
        """Main incident processing workflow"""
        try:
            # Classify the incident
            incident = self.incident_classifier.classify_incident(incident_data)
            
            # Store incident in database
            self._store_incident(incident)
            
            # Generate response plan
            response_steps = self._generate_response_plan(incident)
            
            # Execute response actions
            self._execute_response_plan(incident.incident_id, response_steps)
            
            logging.info(f"Incident {incident.incident_id} processed successfully")
            return incident.incident_id
            
        except Exception as e:
            logging.error(f"Error processing incident: {str(e)}")
            raise
            
    def _store_incident(self, incident: IncidentData):
        """Store incident in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO incidents (
                incident_id, incident_type, severity, detection_time,
                affected_systems, indicators, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident.incident_id,
            incident.incident_type.value,
            incident.severity.value,
            incident.detection_time.isoformat(),
            json.dumps(incident.affected_systems),
            json.dumps(incident.indicators),
            incident.description,
            incident.status
        ))
        
        conn.commit()
        conn.close()
        
    def _generate_response_plan(self, incident: IncidentData) -> List[ResponseStep]:
        """Generate automated response plan based on incident type"""
        steps = []
        
        if incident.incident_type == IncidentType.RANSOMWARE:
            # Isolate all affected systems
            for system in incident.affected_systems:
                steps.append(ResponseStep(
                    action=ResponseAction.ISOLATE_SYSTEM,
                    target=system,
                    parameters={'method': 'edr_isolation'}
                ))
            
            # Block C2 IPs
            c2_ips = incident.indicators.get('c2_ips', [])
            for ip in c2_ips:
                steps.append(ResponseStep(
                    action=ResponseAction.BLOCK_IP,
                    target=ip,
                    parameters={'rule_name': f'BLOCK_C2_{ip.replace(".", "_")}'}
                ))
                
            # Collect forensic evidence
            for system in incident.affected_systems:
                steps.append(ResponseStep(
                    action=ResponseAction.COLLECT_EVIDENCE,
                    target=system,
                    parameters={'evidence_types': ['memory_dump', 'disk_image']}
                ))
                
        elif incident.incident_type == IncidentType.DATA_EXFILTRATION:
            # Block external IPs
            external_ips = incident.indicators.get('external_ips', [])
            for ip in external_ips:
                steps.append(ResponseStep(
                    action=ResponseAction.BLOCK_IP,
                    target=ip,
                    parameters={'rule_name': f'BLOCK_EXFIL_{ip.replace(".", "_")}'}
                ))
                
            # Isolate source system
            for system in incident.affected_systems:
                steps.append(ResponseStep(
                    action=ResponseAction.ISOLATE_SYSTEM,
                    target=system,
                    parameters={'method': 'network_isolation'}
                ))
                
            # Disable compromised account
            user_account = incident.indicators.get('user_account')
            if user_account:
                steps.append(ResponseStep(
                    action=ResponseAction.DISABLE_ACCOUNT,
                    target=user_account,
                    parameters={'domain': 'company.local'}
                ))
                
        elif incident.incident_type == IncidentType.CREDENTIAL_COMPROMISE:
            # Disable compromised accounts
            compromised_accounts = incident.indicators.get('compromised_accounts', [])
            for account in compromised_accounts:
                steps.append(ResponseStep(
                    action=ResponseAction.DISABLE_ACCOUNT,
                    target=account,
                    parameters={'domain': 'company.local'}
                ))
                
            # Block source IP
            source_ip = incident.indicators.get('source_ip')
            if source_ip:
                steps.append(ResponseStep(
                    action=ResponseAction.BLOCK_IP,
                    target=source_ip,
                    parameters={'rule_name': f'BLOCK_ATTACK_{source_ip.replace(".", "_")}'}
                ))
                
        elif incident.incident_type == IncidentType.DDOS_ATTACK:
            # Block attack sources
            attack_sources = incident.indicators.get('attack_sources', [])
            for source in attack_sources:
                steps.append(ResponseStep(
                    action=ResponseAction.BLOCK_IP,
                    target=source,
                    parameters={'rule_name': f'BLOCK_DDOS_{source.replace(".", "_").replace("/", "_")}'}
                ))
                
        # Add notification step for all incidents
        steps.append(ResponseStep(
            action=ResponseAction.NOTIFY_STAKEHOLDERS,
            target="security_team",
            parameters={'incident_id': incident.incident_id, 'severity': incident.severity.value}
        ))
        
        return steps
        
    def _execute_response_plan(self, incident_id: str, steps: List[ResponseStep]):
        """Execute response plan with parallel execution where possible"""
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for step in steps:
                future = executor.submit(self._execute_response_step, incident_id, step)
                futures.append((future, step))
                
            for future, step in as_completed([(f, s) for f, s in futures]):
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    step.status = "completed"
                    step.result = result
                    step.execution_time = datetime.datetime.now()
                    
                except Exception as e:
                    step.status = "failed"
                    step.result = str(e)
                    step.execution_time = datetime.datetime.now()
                    logging.error(f"Response step failed: {str(e)}")
                    
                # Store response action in database
                self._store_response_action(incident_id, step)
                
    def _execute_response_step(self, incident_id: str, step: ResponseStep) -> str:
        """Execute individual response step"""
        
        if step.action == ResponseAction.ISOLATE_SYSTEM:
            method = step.parameters.get('method', 'edr_isolation')
            
            if method == 'edr_isolation':
                success = self.edr_manager.isolate_endpoint(step.target)
            elif method == 'network_isolation':
                success = self.switch_manager.isolate_port_by_ip(step.target)
            else:
                raise ValueError(f"Unknown isolation method: {method}")
                
            return "Success" if success else "Failed"
            
        elif step.action == ResponseAction.BLOCK_IP:
            rule_name = step.parameters.get('rule_name', f'BLOCK_{step.target}')
            success = self.firewall_manager.block_ip_address(step.target, rule_name)
            return "Success" if success else "Failed"
            
        elif step.action == ResponseAction.COLLECT_EVIDENCE:
            evidence_types = step.parameters.get('evidence_types', ['memory_dump'])
            results = []
            
            for evidence_type in evidence_types:
                if evidence_type == 'memory_dump':
                    path = self.forensics_collector.collect_memory_dump(step.target, incident_id)
                elif evidence_type == 'disk_image':
                    path = self.forensics_collector.collect_disk_image(step.target, incident_id)
                elif evidence_type == 'network_logs':
                    path = self.forensics_collector.collect_network_logs(incident_id)
                else:
                    continue
                    
                if path:
                    results.append(f"{evidence_type}: {path}")
                    
            return "; ".join(results) if results else "No evidence collected"
            
        elif step.action == ResponseAction.DISABLE_ACCOUNT:
            # This would integrate with Active Directory or other identity systems
            logging.info(f"Account {step.target} disabled (simulated)")
            return f"Account {step.target} disabled"
            
        elif step.action == ResponseAction.NOTIFY_STAKEHOLDERS:
            # This would integrate with email, Slack, SMS systems
            logging.info(f"Stakeholders notified for incident {incident_id}")
            return "Notifications sent"
            
        else:
            raise ValueError(f"Unknown response action: {step.action}")
            
    def _store_response_action(self, incident_id: str, step: ResponseStep):
        """Store response action in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO response_actions (
                incident_id, action_type, target, parameters,
                status, execution_time, result
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            incident_id,
            step.action.value,
            step.target,
            json.dumps(step.parameters),
            step.status,
            step.execution_time.isoformat() if step.execution_time else None,
            step.result
        ))
        
        conn.commit()
        conn.close()
        
    def get_incident_status(self, incident_id: str) -> Dict[str, Any]:
        """Get incident status and response actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get incident details
        cursor.execute('SELECT * FROM incidents WHERE incident_id = ?', (incident_id,))
        incident_row = cursor.fetchone()
        
        if not incident_row:
            return {"error": "Incident not found"}
            
        # Get response actions
        cursor.execute('SELECT * FROM response_actions WHERE incident_id = ?', (incident_id,))
        action_rows = cursor.fetchall()
        
        conn.close()
        
        # Format response
        incident_data = {
            "incident_id": incident_row[0],
            "incident_type": incident_row[1],
            "severity": incident_row[2],
            "detection_time": incident_row[3],
            "affected_systems": json.loads(incident_row[4]),
            "status": incident_row[7],
            "response_actions": []
        }
        
        for action in action_rows:
            incident_data["response_actions"].append({
                "action_type": action[2],
                "target": action[3],
                "status": action[5],
                "execution_time": action[6],
                "result": action[7]
            })
            
        return incident_data

def main():
    """Main function for testing the incident response system"""
    
    # Initialize the incident response engine
    engine = IncidentResponseEngine("./mock_data/network_topology.yaml")
    
    # Load a sample incident
    with open("./mock_data/incident_scenarios.json", 'r') as f:
        scenarios = json.load(f)
        
    # Process a ransomware incident
    ransomware_incident = scenarios["malware_outbreak"]
    incident_id = engine.process_incident(ransomware_incident)
    
    print(f"Processed incident: {incident_id}")
    
    # Wait a moment and check status
    time.sleep(2)
    status = engine.get_incident_status(incident_id)
    print(f"Incident status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    main()