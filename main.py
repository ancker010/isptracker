import subprocess
from sys import platform
import time
from configparser import ConfigParser
from influxdb import InfluxDBClient

# set up InfluxDB Connection
parser = ConfigParser()
parser.read("isp-outage-tracker.conf")
wait = parser.get("config", "wait")
count = parser.get("config", "count")
debug = parser.get("config", "debug")
# Set up InfluxDB
host = parser.get("influxdb", "host")
port = parser.get("influxdb", "port")
db = parser.get("influxdb", "db")
username = parser.get("influxdb", "username")
password = parser.get("influxdb", "password")
client = InfluxDBClient(host, port, username, password, db)
client.create_database(db)
client.create_retention_policy('awesome_policy', '30d', 3, default=True)
if debug == "1":
    debug = True
else:
    debug = False


def ping(list):
    global debug, count
    updown = []
    for ip in list:
        if platform == "darwin":
            ping_response = subprocess.Popen(["/sbin/ping", f"-c{count}", "-t1", ip],
                                             stdout=subprocess.PIPE).stdout.read()
        elif platform == "linux":
            ping_response = subprocess.Popen(["/bin/ping", f"-c{count}", "-i0.2", "-W1", ip],
                                             stdout=subprocess.PIPE).stdout.read()
        if debug == 1:
            print(ping_response)
        if "ttl" in str(ping_response):
            updown.append("up")
        else:
            updown.append("down")

    if "up" in updown:
        if debug == 1:
            print("Up!")
        return True
    else:
        if debug == 1:
            print("Down!")
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

    # Tries to write to the database
    success = False
    while not success:
        try:
            client.write_points(point)
            success = True
        except:
            print("An exception occurred while writing to database")
            success = False
            # Waits 1 sec before next try
            time.sleep(1)


if __name__ == "__main__":
    # Print some startup messages...
    print(f"Starting up...\nWait: {wait} - Count: {count}")
    print(f"InfluxDB: {host}:{port} - DB: {db}")

    # Print info for each ISP...
    for section in parser.sections():
        if 'isp' in str(section):
            print(parser.get(section, "name") + ": " + parser.get(section, "ip1") + ", " + parser.get(section, "ip2"))
        else:
            continue

    isplist = []
    for section in parser.sections():
        if 'isp' in str(section):
            isplist.append(str(section))

    # Do the stuff.
    while True:
        for section in isplist:
            if 'isp' in section:
                iplist = []
                name = parser.get(section, "name")
                ip1 = parser.get(section, "ip1")
                ip2 = parser.get(section, "ip2")
                iplist.append(ip1)
                iplist.append(ip2)
                if debug == 1:
                    print(f"{name}: {iplist}")
                if ping(iplist):
                    isp = "up"
                else:
                    isp = "down"
                if debug == 1:
                    print(f"{name}: is {isp}!")
                if debug == 0:
                    write_database(name, isp)

        time.sleep(int(wait))
