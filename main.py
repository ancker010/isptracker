import subprocess
from sys import platform
import time
from configparser import ConfigParser
from influxdb import InfluxDBClient

# set up InfluxDB Connection
parser = ConfigParser()
parser.read("isp-outage-tracker.conf")
# Set up InfluxDB
host = parser.get("influxdb", "host")
port = parser.get("influxdb", "port")
wait = parser.get("config", "wait")
count = parser.get("config", "count")
db = parser.get("influxdb", "db")
username = parser.get("influxdb", "username")
password = parser.get("influxdb", "password")
client = InfluxDBClient(host, port, username, password, db)
client.create_database(db)
client.create_retention_policy('awesome_policy', '30d', 3, default=True)


def ping(list):
    updown = []
    for ip in list:
        if platform == "darwin":
            ping_response = subprocess.Popen(["/sbin/ping", f"-c{count}", "-t1", list[0]],
                                             stdout=subprocess.PIPE).stdout.read()
        elif platform == "linux":
            ping_response = subprocess.Popen(["/bin/ping", f"-c{count}", "-W1", list[0]],
                                             stdout=subprocess.PIPE).stdout.read()
        if "ttl" in str(ping_response):
            updown.append("up")
        else:
            updown.append("down")

    if "up" in updown:
        # print("Up!")
        return True
    else:
        # print("Down!")
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

    # Do the stuff.
    while True:
        for section in parser.sections():
            if 'isp' in str(section):
                iplist = []
                name = parser.get(section, "name")
                ip1 = parser.get(section, "ip1")
                ip2 = parser.get(section, "ip2")
                iplist.append(ip1)
                iplist.append(ip2)
                if ping(iplist):
                    isp = "up"
                else:
                    isp = "down"
                #print(f"{name}: is {isp}!")
                write_database(name, isp)

        time.sleep(int(wait))
