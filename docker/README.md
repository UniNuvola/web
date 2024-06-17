# Vault in a Docker Conainer 🐋

This folder contains the config files for run Vault within a Docker Container.
This configuration is designed to run Vault in _Server mode_,
so that any information and configurations are persisted at every restart.
Each time the Docker container starts up, Vault will start in _Sealed mode_, allowing any operation to be performed
by undergoing an Unsealing procedure. This procedure is automated by the `auto_unseal.py` script.
To enable execution of this script, save the JSON file containing various keys generated during Vault's initialization phase
within this folder and rename it  `.env`.
Finally, start the procedure with

```bash
python auto_unseal.py
```

More automation script must be added !
