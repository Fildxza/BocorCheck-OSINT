#!/usr/bin/env python3
"""Test mitigation functions"""

from mitigation import get_malaysian_resources, get_smart_recommendations

resources = get_malaysian_resources()
print(f'✅ Malaysian resources: {len(resources)} found')
for r in resources[:3]:
    print(f'   - {r.get("resource_name")}')

recs = get_smart_recommendations(['Email', 'Password'], 'HIGH')
print(f'\n✅ Smart recommendations:')
print(f'   - Critical actions: {len(recs.get("critical_actions", []))}')
print(f'   - Important actions: {len(recs.get("important_actions", []))}')
print(f'   - Estimated time: {recs.get("estimated_total_time")}')
