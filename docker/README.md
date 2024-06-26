# Vault in a Docker Container 🐋

This folder contains the config files for run Vault within a Docker Container.
This configuration is designed to run Vault in _Server mode_,
so that any information and configurations are persisted at every restart.
Each time the Docker container starts up, Vault will start in _Sealed mode_, allowing any operation to be performed
by undergoing an Unsealing procedure. This procedure, as well as all the deploy process, is automated by the `vault.py` cli tool.

## CLI tool and Auto-deploy

This script is designed to manage the creation of a new instance of Vault entirely autonomously.
It can be launched as a single command to perform the entire procedure or invoked step-by-step for specific needs.
For now, commands do not accept parameters, but in the future it may be modified to make everything more
general and complete.

The script will automatically generate the `.env` file containing access keys to Vault and necessary for running some
commands in standalone mode.

```
Usage: vault.py [OPTIONS] COMMAND [ARGS]...

  Vault CLI tools to auto-deploy a new Vault container.

Options:
  --verbose [info|debug]  Logging level
  --help                  Show this message and exit.

Commands:
  create-entity    Creates entities.
  create-group     Create the default group.
  deploy           Deploy procedure.
  enable-userpass  Enable userpass/ auth method.
  init             Initialize Vault when first created.
  set-users        Set userpass/ users.
  unseal           Unseal the Vault.
```

To deploy a new Vault container, start the container and then run the script:

```bash
docker compose up -d
python vault.py deploy
```

