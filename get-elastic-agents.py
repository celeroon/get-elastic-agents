import requests
import pandas as pd
import getpass
from datetime import datetime

fleet_server_agnets_status = dict()
kibana_ip = input('Kibana IP address: ')
# kibana_username = input('Kibana username: ')
# kibana_password = getpass.getpass(prompt='Kibana password: ')
kibapa_api = input('Kibana API key: ')

for page in range(1,1000):
    r = requests.get(f'https://{kibana_ip}:5601/api/fleet/agents?perPage=20&page={page}',
                    # auth=(kibana_username,kibana_password),
                    headers={
                        'Content-Type':'application/json;charset=UTF-8',
                        'kbn-xsrf': 'true',
                        'Authorization':f'ApiKey {kibapa_api}'
                    },
                    verify=False)
    
    results = r.json()
    df = pd.DataFrame(results)
    df_len = df.shape[0]
    if df_len:
        df_items = pd.json_normalize(df['items'])
        df_hosts_status = df_items[['enrolled_at','local_metadata.host.name','status']]
        df_to_dict = df_hosts_status.to_dict(orient='list')
        for keys,values in df_to_dict.items():

            for value in values:

                fleet_server_agnets_status.setdefault(keys,[]).append(value)
    else:
        break


today_date = datetime.today().strftime('%Y-%m-%d')
df_fleet_server_agnets_status = pd.DataFrame(fleet_server_agnets_status).to_csv(f'{today_date}_fleet_server_agents_status.csv',index=False)
