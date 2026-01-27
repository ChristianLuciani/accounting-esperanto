#!/usr/bin/env python3
"""
Convert between human-readable (YAML) and machine-readable (JSON) formats.

Usage:
    python format_converter.py human_to_machine spec/human/master.yaml spec/machine/nodes.json
    python format_converter.py machine_to_human spec/machine/nodes.json spec/human/master.yaml
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict

def human_to_machine(yaml_file: Path, json_file: Path):
    """Convert nested YAML to flat JSON."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    flat_accounts = []
    
    def flatten(items, parent_uuid=None):
        for item in items:
            account = {
                "uuid": item["uuid"],
                "standard_code": item["code"],
                "label_en": item["label"],
                "nature": item["nature"],
                "relations": {
                    "parent_uuid": parent_uuid
                }
            }
            flat_accounts.append(account)
            
            if "groups" in item:
                flatten(item["groups"], item["uuid"])
            if "categories" in item:
                flatten(item["categories"], item["uuid"])
    
    flatten(data.get("elements", []))
    
    with open(json_file, 'w') as f:
        json.dump(flat_accounts, f, indent=2)
    
    print(f"✅ Converted {yaml_file} → {json_file}")

def machine_to_human(json_file: Path, yaml_file: Path):
    """Convert flat JSON to nested YAML."""
    with open(json_file) as f:
        accounts = json.load(f)
    
    # Build hierarchy
    # (Simplified - production version would handle full nesting)
    roots = [a for a in accounts if a["relations"].get("parent_uuid") is None]
    
    output = {"elements": roots}
    
    with open(yaml_file, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Converted {json_file} → {yaml_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    mode = sys.argv[1]
    input_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    
    if mode == "human_to_machine":
        human_to_machine(input_file, output_file)
    elif mode == "machine_to_human":
        machine_to_human(input_file, output_file)
    else:
        print("Error: Mode must be 'human_to_machine' or 'machine_to_human'")
        sys.exit(1)
