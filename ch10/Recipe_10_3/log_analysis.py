import re
from collections import defaultdict
from datetime import datetime, timedelta

LOG_FILE = "mock_data/firewall_logs.txt"
TIME_WINDOW = timedelta(minutes=1)  # 1 minute window for detection
PORT_SCAN_THRESHOLD = 5  # Number of ports accessed in window
BRUTE_FORCE_THRESHOLD = 5  # Number of denied attempts in window

def parse_log_line(line):
    # Adjust regex to match your log format
    match = re.match(r"(\S+) (\S+) (\S+) (\d+) (\S+)", line)
    if match:
        timestamp, src_ip, dst_ip, dst_port, action = match.groups()
        return {
            "timestamp": datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "dst_port": int(dst_port),
            "action": action
        }
    return None

def detect_threats(logs):
    port_scan_candidates = defaultdict(list)
    brute_force_candidates = defaultdict(list)

    for entry in logs:
        # For port scan: group by src_ip and dst_ip
        key = (entry["src_ip"], entry["dst_ip"])
        port_scan_candidates[key].append((entry["timestamp"], entry["dst_port"]))

        # For brute force: group by src_ip, dst_ip, dst_port, and action
        if entry["action"].upper() == "DENY":
            bf_key = (entry["src_ip"], entry["dst_ip"], entry["dst_port"])
            brute_force_candidates[bf_key].append(entry["timestamp"])

    # Detect port scans
    port_scans = []
    for key, attempts in port_scan_candidates.items():
        attempts.sort()
        ports = set()
        window_start = attempts[0][0] if attempts else None
        for ts, port in attempts:
            if window_start and ts - window_start > TIME_WINDOW:
                window_start = ts
                ports = set()
            ports.add(port)
            if len(ports) >= PORT_SCAN_THRESHOLD:
                port_scans.append({"src_ip": key[0], "dst_ip": key[1], "ports": list(ports)})
                break

    # Detect brute force
    brute_forces = []
    for key, times in brute_force_candidates.items():
        times.sort()
        window = []
        for ts in times:
            window = [t for t in window if ts - t <= TIME_WINDOW]
            window.append(ts)
            if len(window) >= BRUTE_FORCE_THRESHOLD:
                brute_forces.append({"src_ip": key[0], "dst_ip": key[1], "dst_port": key[2]})
                break

    return port_scans, brute_forces

def main():
    try:
        with open(LOG_FILE) as f:
            logs = [parse_log_line(line) for line in f if parse_log_line(line)]
    except FileNotFoundError:
        print(f"Log file {LOG_FILE} not found.")
        return

    port_scans, brute_forces = detect_threats(logs)

    print("Port Scans Detected:")
    for scan in port_scans:
        print(scan)

    print("\nBrute Force Attacks Detected:")
    for bf in brute_forces:
        print(bf)

if __name__ == "__main__":
    main()
