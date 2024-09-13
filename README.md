# python-bot

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
```bash
pip install -r requirements.txt
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
To use the bot, you must get a key provided by https://t.me/BotFather


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


## Setting up debian machine

### First of all add bot user to the sudoers group
Edit the sudores file
```bash
sudo visudo
```
Put this line at the end of the file
```bash
bot ALL=(ALL:ALL) ALL
```

### Install VSCode and Git
```bash
sudo apt update
sudo apt upgrade
```
#### VSCode
Run this commands
```bash
sudo apt install software-properties-common apt-transport-https wget -y
```
```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/packages.microsoft.gpg
```
```bash
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
```
Install vscode
```bash
sudo apt update
sudo apt install code
```

#### Git
Install git
```bash
sudo apt update
sudo apt install git -y
```
Set credentials
```bash
git config --global user.name "NabilHG"
git config --global user.email "nabilhajjoune@gmail.com"
```
Verify credentials
```bash
git config --global --list
```

### Reboot!
```bash
sudo reboot now
```

### Install OpenVPN
```bash
sudo apt update
sudo apt upgrade
```
Install openvpn
```bash
sudo apt install openvpn
```

#### Add /usr/sbin to the PATH permanently
Edit ~/.bashrc file
```bash
nano ~/.bashrc
```
Add the next line at the end
```bash
export PATH=$PATH:/usr/sbin
```

### Allow bot user to execute openvpn and pkill without sudo
Edit visudo file
```bash
sudo visudo
```
Add the next line at the end
```bash
bot ALL=(ALL) NOPASSWD: /usr/sbin/openvpn, /usr/bin/pkill
```

### Reboot!
```bash
sudo reboot now
```

### To start coding
The following steps is to set up the enviroment to start coding

#### Clone the repository
```bash
git clone https://github.com/NabilHG/Bot_Project.git 
```
Change directory into Bot_Project folder, the run the following command
```bash
sudo apt install python3.11-venv
```
Create the virtual enviroment
```bash
python3 -m venv myenv
```
Activate the virtual enviroment
```bash
source myenv/bin/activate
```
Run the following commands to install all the necesary dependencies
```bash
pip install --upgrade pip setuptools
```
```bash
pip install -r requirements.txt
```

Launch code
```bash
python3 main.py
```

## The Git object files have gone corrupt
This can happen during machine crashes, etc.

#### Try to save the changes as you can, just in case!

### Execute the following commands
This will first remove any empty object files that cause corruption of the repository as a whole.
```bash
find .git/objects/ -type f -empty -delete
```
Then fetch down the missing objects (as well as latest changes) from the remote repository.
```bash
git fetch -p
```
Then do a full object store check. Which, at this point, should succeed without any errors (there may be still some warnings though!)
```bash
git fsck --full
```

## MySQL Installation

Run the following commands:
```bash
wget https://dev.mysql.com/get/mysql-apt-config_0.8.30-1_all.deb
```
```bash
sudo dpkg -i mysql-apt-config_0.8.30-1_all.deb
```
```bash
sudo apt update
```
Then
```bash
sudo apt install mysql-server
```
This error will appear probably
```bash
Error: Unable to correct problems, you have held broken packages.
```
So install libssl1.1_1.1.1w-0+deb11u1_amd64.deb, via Debian packages: 
```bash
https://packages.debian.org/bullseye/amd64/libssl1.1/download
```
Navegate to /Downloads and install the package
```bash
sudo dpkg -i libssl1.1_1.1.1w-0+deb11u1_amd64.deb
```
```bash
sudo apt --fix-broken install
```
```bash
sudo apt update
```

Install mysql-server
```bash
sudo apt install -y mysql-server
```
Verify
```bash
sudo systemctl status mysql
```
Secure config of mysql
```bash
sudo mysql_secure_installation
```

### Workbench(via snapd):
```bash
sudo apt update
```
```bash
sudo apt install snapd
```
```bash
sudo snap install snapd
```
```bash
sudo snap install mysql-workbench-community
```
Run app: 
```bash
snap run mysql-workbench-community
```

### Aerich
Install aerich for migrations
```bash
pip install aerich
```
Initialized database
```bash
aerich --app models init-db
```
For doing migration
```bash
aerich migrate --name drop_column
```
For aplying the migration
```bash
aerich upgrade
```
For returning to the past migration
```bash
aerich downgrade
```