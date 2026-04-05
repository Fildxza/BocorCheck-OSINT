#!/usr/bin/env python3
import os

file_path = 'templates/breach_timeline.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script closing tag
pos = content.find('</script>')
if pos != -1:
    cleaned = content[:pos+9] + '\n{% endblock %}'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print('✓ File cleaned successfully!')
    print(f'File size: {len(cleaned)} bytes')
else:
    print('✗ Could not find </script>')
