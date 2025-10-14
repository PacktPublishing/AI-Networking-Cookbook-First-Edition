# script2_create_training_data.py
import json

training_examples = [
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Configure BGP for AS 65001 with neighbor 192.168.1.2 in AS 65002"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.1.1.1 255.255.255.255\n!\nrouter bgp 65001\n bgp router-id 10.1.1.1\n bgp log-neighbor-changes\n neighbor 192.168.1.2 remote-as 65002\n neighbor 192.168.1.2 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Set up BGP for AS 65010 with neighbor 10.0.1.1 in AS 65020"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.10.1.1 255.255.255.255\n!\nrouter bgp 65010\n bgp router-id 10.10.1.1\n bgp log-neighbor-changes\n neighbor 10.0.1.1 remote-as 65020\n neighbor 10.0.1.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Configure BGP AS 65100 with neighbor 172.16.1.1 AS 65200"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.100.1.1 255.255.255.255\n!\nrouter bgp 65100\n bgp router-id 10.100.1.1\n bgp log-neighbor-changes\n neighbor 172.16.1.1 remote-as 65200\n neighbor 172.16.1.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Setup BGP for AS 65300 with neighbor 203.0.113.1 AS 65400"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.30.1.1 255.255.255.255\n!\nrouter bgp 65300\n bgp router-id 10.30.1.1\n bgp log-neighbor-changes\n neighbor 203.0.113.1 remote-as 65400\n neighbor 203.0.113.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Configure BGP AS 65500 with peer 198.51.100.1 AS 65600"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.50.1.1 255.255.255.255\n!\nrouter bgp 65500\n bgp router-id 10.50.1.1\n bgp log-neighbor-changes\n neighbor 198.51.100.1 remote-as 65600\n neighbor 198.51.100.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Create BGP config for AS 65700 connecting to 192.0.2.1 AS 65800"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.70.1.1 255.255.255.255\n!\nrouter bgp 65700\n bgp router-id 10.70.1.1\n bgp log-neighbor-changes\n neighbor 192.0.2.1 remote-as 65800\n neighbor 192.0.2.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "BGP configuration for AS 65900 with neighbor 10.255.1.1 AS 66000"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.90.1.1 255.255.255.255\n!\nrouter bgp 65900\n bgp router-id 10.90.1.1\n bgp log-neighbor-changes\n neighbor 10.255.1.1 remote-as 66000\n neighbor 10.255.1.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Set up BGP AS 66100 peering with 172.31.1.1 AS 66200"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.61.1.1 255.255.255.255\n!\nrouter bgp 66100\n bgp router-id 10.61.1.1\n bgp log-neighbor-changes\n neighbor 172.31.1.1 remote-as 66200\n neighbor 172.31.1.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Configure BGP for AS 66300 with external peer 209.165.200.1 AS 66400"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.63.1.1 255.255.255.255\n!\nrouter bgp 66300\n bgp router-id 10.63.1.1\n bgp log-neighbor-changes\n neighbor 209.165.200.1 remote-as 66400\n neighbor 209.165.200.1 activate"}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "You are a network engineer. Always use Loopback0 for BGP router-id and enable log-neighbor-changes."},
            {"role": "user", "content": "Setup BGP routing for AS 66500 connecting to 203.0.113.254 AS 66600"},
            {"role": "assistant", "content": "interface Loopback0\n description BGP_ROUTER_ID\n ip address 10.65.1.1 255.255.255.255\n!\nrouter bgp 66500\n bgp router-id 10.65.1.1\n bgp log-neighbor-changes\n neighbor 203.0.113.254 remote-as 66600\n neighbor 203.0.113.254 activate"}
        ]
    }
]

with open('bgp_training_data.jsonl', 'w') as f:
    for example in training_examples:
        f.write(json.dumps(example) + '\n')

print("Training data created: bgp_training_data.jsonl")
print(f"Total examples: {len(training_examples)}")