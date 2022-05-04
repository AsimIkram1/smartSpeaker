# Installation
The following steps were tested on Ubuntu 21.04 with python 3. These will need to be performed for all systems that run the code
1. Create a python virtual environment and activate that
```
python3 -m venv realtime
```
2. Install required packages
```
pip install -r requirements.txt
```

# How to Run
1. Edit the config.yaml file on all machines. The fields are explained below
- bluetooth: List of bluetooth devices to connect to
- ips: List of wifi devices to connect to
- host: beacon that determines distance

A bit of explaination as to why we need these lists. Lets say you want to connect two bluetooth speakers to raspberry pi 1 and a wired speaker to raspberry pi 2, you would have different configuration files for both of these. for Pi 1, you would add the names of both speakers to the bluetooth list and for Pi 2, you would leave that list empty. This way, Pi 1 will not start playing music till both the speakers are connected to it but Pi 2 will not be held back by this condition.

2. Run the code on the machines
- Since we have a barrier that runs over the network, one machine needs to act as the server. Select the one that you want to make the server and run that one first. Run the other machine after the server has started. There is a limitation where the IP of the server if hardcoded for the clients. This will need to manually changed in the code

3. Move the beacon closer or away from the device. The speakers should respond accordingly.