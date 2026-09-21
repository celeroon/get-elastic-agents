# get-elastic-agents
Get agetns status to csv

## Usage
```bash
python3 -m venv venv
source venv/bin/activate
pip install requests pandas
python get-elastic-agents.py
```
Enter your Kibana IP and API key when prompted. Output: `YYYY-MM-DD_fleet_server_agents_status.csv`.
