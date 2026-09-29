#!/usr/bin/env python3

import json
import os
import subprocess
import sys

os.makedirs("data", exist_ok=True)

result = subprocess.run("hugo list all", shell=True, capture_output=True, text=True)
if result.returncode != 0:
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

lines = result.stdout.splitlines()

content_lines = lines[1:]
filtered_lines = [line for line in content_lines if not line.startswith("WARN  ")]

count = str(len(content_lines))

dates = [line.split(",")[3] for line in filtered_lines if len(line.split(",")) > 3]
dates.sort(reverse=True)
latest = dates[0] if dates else ""

stats = {"count": count, "latest": latest}

with open("data/stats.json", "w") as f:
    json.dump(stats, f)

print("Wrote data/stats.json:")
print(json.dumps(stats))
