import subprocess
from sys import platform
import time
from configparser import ConfigParser
from influxdb import InfluxDBClient

## set up InfluxDB Connection
parser = ConfigParser()
parser.read("isp-outage-tracker.conf")
# Set up InfluxDB
host = parser.get("influxdb", "host")
port = parser.get("influxdb", "port")
db = parser.get("influxdb", "db")
username = parser.get("influxdb", "username")
password = parser.get("influxdb", "password")
client = InfluxDBClient(host, port, username, password, db)
client.create_database(db)
client.create_retention_policy('awesome_policy', '30d', 3, default=True)


def ping_isp1(list):
    if platform == "darwin":
        ping_response1 = subprocess.Popen(["/sbin/ping", "-c2", "-t1", list[0]],
                                         stdout=subprocess.PIPE).stdout.read()
    elif platform == "linux":
        ping_response1 = subprocess.Popen(["/bin/ping", "-c2", "-W1", list[0]],
                                         stdout=subprocess.PIPE).stdout.read()
    if platform == "darwin":
        ping_response2 = subprocess.Popen(["/sbin/ping", "-c2", "-t1", list[1]],
                                         stdout=subprocess.PIPE).stdout.read()
    elif platform == "linux":
        ping_response2 = subprocess.Popen(["/bin/ping", "-c2", "-W1", list[1]],
                                         stdout=subprocess.PIPE).stdout.read()
    if "ttl" in str(ping_response1) and "ttl" in str(ping_response2):
        # print("ISP1: Up!")
        return True
    else:
        # print("ISP1: Down!")
        return False


def ping_isp2(list):
    if platform == "darwin":
        ping_response1 = subprocess.Popen(["/sbin/ping", "-c2", "-t1", list[0]],
                                          stdout=subprocess.PIPE).stdout.read()
    elif platform == "linux":
        ping_response1 = subprocess.Popen(["/usr/bin/ping", "-c2", "-W1", list[0]],
                                          stdout=subprocess.PIPE).stdout.read()
    if platform == "darwin":
        ping_response2 = subprocess.Popen(["/sbin/ping", "-c2", "-t1", list[1]],
                                          stdout=subprocess.PIPE).stdout.read()
    elif platform == "linux":
        ping_response2 = subprocess.Popen(["/usr/bin/ping", "-c2", "-W1", list[1]],
                                          stdout=subprocess.PIPE).stdout.read()
    if "ttl" in str(ping_response1) and "ttl" in str(ping_response2):
        # print("ISP2: Up!")
        return True
    else:
        # print("ISP2: Down!")
        return False


def write_database(isp, status):
    point = [{}]
    point[0]['tags'] = {}
    point[0]['fields'] = {}
    point[0]['measurement'] = "isptracker"
    point[0]['tags']['isp'] = isp
    point[0]['tags']['status'] = status

    # The field percent_packet_loss depends enterely of the parameter status
    if status == 'up':
        percent_packet_loss = 0
    else:
        percent_packet_loss = 100

    point[0]['fields']['percent_packet_loss']=percent_packet_loss

    #Tries to write to the database
    success = False
    while not success:
        try:
            client.write_points(point)
            success = True
        except:
            print("An exception occurred while writing to database")
            success = False
            #Waits 1 sec before next try
            time.sleep(1)


if __name__ == "__main__":
    isp1_list = []
    isp2_list = []
    # Gather IPs to ping for each ISP
    isp1_name = parser.get("isp1", "name")
    isp1_ip1 = parser.get("isp1", "ip1")
    isp1_ip1 = parser.get("isp1", "ip2")
    isp2_ip1 = parser.get("isp2", "ip1")
    isp2_ip1 = parser.get("isp2", "ip2")
    isp1_list.append(isp1_ip1)
    isp1_list.append(isp1_ip1)
    isp2_name = parser.get("isp2", "name")
    isp2_list.append(isp2_ip1)
    isp2_list.append(isp2_ip1)

    while True:
        if ping_isp1(isp1_list):
            isp1 = "up"
        else:
            isp1 = "down"
        if ping_isp2(isp2_list):
            isp2 = "up"
        else:
            isp2 = "down"

        write_database(isp1_name, isp1)
        write_database(isp2_name, isp2)
        #print(f"{isp1_name}: {isp1} - {isp2_name}: {isp2}")
        time.sleep(5)
