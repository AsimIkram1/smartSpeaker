from tabnanny import verbose
from time import sleep
import scapy.all as scapy
import threading
import yaml
from pydub import AudioSegment
from pydub.playback import play
import subprocess
from pydub.playback import _play_with_simpleaudio
import socket   

ip_connected = False
bt_connected = False
range_valid = False
playback = None
ip_counter=0
bt_counter=0
sound_player_running = False
synced = False

def client():
    s = socket.socket()        
    port = 5555               
    s.connect(('192.168.2.104', port))
    while True:
        response = s.recv(1024).decode()
        if('connected' in response):
            s.send('connected'.encode())
            break
    s.close()  

def read_file():
    ip_list = []
    with open('config.yaml', 'r') as ip_file:
        try:
            ip_list = yaml.safe_load(ip_file)
        except Exception as e:
            print(e)

    return ip_list['ips'], ip_list['bluetooth'], ip_list['host']

def scanner(ip_list):
    try:
        global ip_counter
        for ip in ip_list:
            cmd = 'iwgetid | grep "' + ip + '"'
            output = subprocess.check_output(cmd, shell=True)
            output = output.decode('utf-8')
            global ip_connected
            global is_playing

            try:
                if(ip in output):
                    ip_counter += 1

            except:
                # ip_connected = False
                is_playing = False
                ip_counter -= 1

        if(ip_counter >= len(ip_list)):
            ip_counter = 0
            ip_connected = True
        else:
            ip_connected = False

    except Exception as e:
        # This means no ip devices were connected
        ip_connected = True

def bluetooth_scanner(bt_list):
    try:
        global bt_counter
        for bt in bt_list:
            cmd = 'bluetoothctl paired-devices | grep "' + bt + '"'
            output = subprocess.check_output(cmd, shell=True)
            output = output.decode('utf-8')
            global bt_connected
            if(bt in output):
                bt_counter += 1
                # bt_connected = True
            else:
                bt_counter -= 1
                # bt_connected = False
        
        if(bt_counter >= len(bt_list)):
            bt_counter = 0
            bt_connected = True
        else:
            bt_connected = False

    except Exception as e:
        # This means no bt devices were listed
        bt_connected = True

def distance_scanner_bt(host):
    try:
        global range_valid
        cmd = 'bluetoothctl paired-devices | grep "' + host + '"' + " | awk '{print $2}'"
        output = subprocess.check_output(cmd, shell=True)
        mac = output.decode('utf-8')
        rssi_command = 'hcitool rssi ' + mac
        rssi = subprocess.check_output(rssi_command, shell=True)
        rssi = rssi.decode('utf-8')
        rssi = rssi.split(':')[-1].replace('\n','')
        rssi = int(rssi)
        print(rssi)
        range_valid = True if (rssi > 0) else False
    except Exception as e:
        print(e)

def distance_scanner_wifi(host):
    try:
        global range_valid
        # Get interace name
        interface_cmd = 'iwgetid | grep "' + host + '"' + " | awk '{print $1}'"
        interface = subprocess.check_output(interface_cmd, shell=True)
        interface = interface.decode('utf-8').replace('\n','')
        # Get RSSI
        rssi_cmd = 'iwconfig ' + interface + ' | grep Signal'
        rssi_output = subprocess.check_output(rssi_cmd, shell=True)
        rssi_output = rssi_output.decode('utf-8')
        rssi_output = rssi_output.split('Signal level=')[-1]
        rssi_output = rssi_output.split('dBm')[0]
        rssi = int(rssi_output)
        # print(rssi)
        if (rssi > -42):
            range_valid = True
            # print('In range')
        elif (rssi <= -42):
            range_valid = False
            # print('Out of range')
    except Exception as e:
        pass


def rewrite_config(ip_list, bluetooth_list):
    ip_dict = {'ips':ip_list, 'bluetooth': bluetooth_list}
    with open('config.yaml', 'w') as file:
        yaml.dump(ip_dict, file)


def sound_player():
    global playback
    sound = AudioSegment.from_file('sample.mp3')
    playback = _play_with_simpleaudio(sound)
    global sound_player_running
    sound_player_running = True
    # print('playing')
    # if(not ip_connected):
    #     is_playing = False


def main():
    is_playing = False
    ip_list, bluetooth_list, host = read_file()
    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ true", shell=True)
    client()
    print("connected")
    sleep(2.5)
    sound_player()

    while(True):
        # ip_thread = threading.Thread(target=scanner, args=(ip_list,))
        # ip_thread.start()

        # bt_thread = threading.Thread(target=bluetooth_scanner, args=(bluetooth_list,))
        # bt_thread.start()
        scanner(ip_list)
        bluetooth_scanner(bluetooth_list)

        # threading.Thread(target=distance_scanner_wifi, args=(host,)).start()
        distance_scanner_wifi(host)
        if(ip_connected and bt_connected and range_valid):
            while(not is_playing):
                is_playing = True
                # print("All devices connected")
                # print("Play")
                subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ false", shell=True)
        else:
            if((not ip_connected) or (not bt_connected) or (not range_valid)):
                try:
                    # print("Mute")
                    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ true", shell=True)
                    # playback.stop()
                    # print('stopped')
                    is_playing = False
                except:
                    is_playing = False
                    pass

if __name__ == "__main__":
    main()