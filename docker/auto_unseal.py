import os
import json
import subprocess


# load only needed keys
with open('.env') as f:
    secrets = json.load(f)['keys'][:3]

# unseal the vault
for sec in secrets:
    subprocess.run(['docker', 'exec', 'vault', 'vault',  'operator', 'unseal', f'{sec}'])
