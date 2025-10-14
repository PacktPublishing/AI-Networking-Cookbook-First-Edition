#!/usr/bin/env python3
"""
Simple script to convert dot file to PNG topology visualization
"""

import subprocess
import sys

dot_file = sys.argv[1]
output_file = "topology.png"

# Generate PNG from dot file
subprocess.run(['dot', '-Tpng', dot_file, '-o', output_file])

print(f"Generated {output_file}")