import ipaddress
from datetime import datetime

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

kibana_ip = input('Kibana IP address: ')
kibana_api = input('Kibana API key: ')

PER_PAGE = 100


def clean_ips(raw_ips):
    """Keep only usable IPv4 addresses (drop loopback, link-local, IPv6)."""
    result = []
    for entry in raw_ips or []:
        try:
            addr = ipaddress.ip_interface(entry).ip
        except ValueError:
            continue
        if addr.version != 4 or addr.is_loopback or addr.is_link_local:
            continue
        result.append(str(addr))
    return result


rows = []
page = 1
while True:
    r = requests.get(
        f'https://{kibana_ip}:5601/api/fleet/agents?perPage={PER_PAGE}&page={page}',
        headers={
            'Content-Type': 'application/json;charset=UTF-8',
            'kbn-xsrf': 'true',
            'Authorization': f'ApiKey {kibana_api}',
        },
        verify=False,
    )
    r.raise_for_status()
    items = r.json().get('items', [])
    if not items:
        break

    for item in items:
        host = (item.get('local_metadata') or {}).get('host') or {}
        agent = (item.get('local_metadata') or {}).get('elastic', {}).get('agent', {})
        rows.append({
            'enrolled_at': item.get('enrolled_at'),
            'local_metadata.host.name': host.get('name'),
            'status': item.get('status'),
            'agent.version': (item.get('agent') or {}).get('version') or agent.get('version'),
            'local_metadata.host.ip': ';'.join(clean_ips(host.get('ip'))),
        })
    page += 1

today_date = datetime.today().strftime('%Y-%m-%d')
pd.DataFrame(rows).to_csv(f'{today_date}_fleet_server_agents_status.csv', index=False)
print(f'Saved {len(rows)} agents')
