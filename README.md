# python-bot-skeleton
This is a simple skeleton for a python bot using the python-telegram-bot library. It is intended to be used as a starting point for a bot project.

## Virtual Environment
To create a custom virtual environment for your dependencies to be contained, you can use the following command:
```bash
python3 -m venv .myenv 
```
then you must 'use' that environment in the terminal with the following command:
```bash
source myenv/bin/activate
```
you will now be using that virtual environment. 

### Having problems with virtual enviroment?
Try to eliminate, create and update:

Eliminate
```bash
sudo rm -rf myenv/
```

Create
```bash
python3 -m venv myenv
```

Activate
```bash
source myenv/bin/activate
```

Update
```bash
pip install --upgrade pip setuptools
```

## Dependencies
The first time you use the virtual environment, you will need to install the aiogram dependencies, already inside requierements.txt
```bash
pip install -r requirements.txt
```

You can install other dependencies with the following command:
```bash
pip install [package-name]
```
After you finish developing, you have to generate a requirements.txt with:
```bash
pip freeze > requirements.txt
```
### bot_token.txt
To use the bot, you must get a key provided by https://t.me/BotFather, then you shall place it inside a file called bot_token.txt (currently there is an example)
TODO: change this to an environment variable


## Deploy (Docker)
The Dockerfile contains the base settings, the python container version and the start script

The compose.yaml file contains the environment variables and the port to be exposed; as is, it only describes a 'bot' container that will restart always.

To deploy the bot through docker-compose, you can use the following command:
```bash
sudo docker-compose up --build --remove-orphans -d
```
which builds and starts the docker container in the background.
You can use a custom script to backup before deploying the latter command.

## PowerShell Commands
(Every time you have to activate the virtual enviroment, do the following)

Getting the current state for executing script to activate virtual env
```bash
Get-ExecutionPolicy
```

Changing it to be able to do it
```bash
Set-ExecutionPolicy RemoteSigned
```

Changing it back to restricted for safety reasons
```bash
Set-ExecutionPolicy Restricted
```

### Cmd altenative

Navegate to the correct path of the enviroment and run the activation script
```bash
bot_VirtualEnv\Scripts\activate
```
