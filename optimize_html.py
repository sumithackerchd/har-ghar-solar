import os
import re

for root, _, files in os.walk('/workspace/app-d7ekzsh62ku9/templates'):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r') as f:
                content = f.read()

            # Add loading="lazy" to imgs that don't have loading attribute
            content = re.sub(r'<img(?![^>]*loading=)([^>]+)>', r'<img loading="lazy"\1>', content)
            
            # Make sure aria-labels are present on links without text
            # (Basic heuristic, might be complex for regex, skipping complex ones, but keeping basic optimizations)

            with open(filepath, 'w') as f:
                f.write(content)

print("HTML optimized.")
