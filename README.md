### ISP Outage Tracker 
This script and docker image is a very simple method for tracking how often your ISP service(s) are down.

The tool will send two (2) ICMP echo (ping) packets to each of the IPs listed for each ISP configured.
If either or both of these IPs receive a response, then the ISP will be considered "up".
If both of these IPs do not receive a response, the ISP will be considered "down".

It will write a ISP status every N seconds to InfluxDB, which you can then visualize with Grafana or another graphing tool.


#### Usage

- Pull the image: `docker pull hardenrm/isptracker`
- Copy the example conf file to `isp-outage-tracker.conf` and edit it with your info.
- NOTE: You may set only two ISPs at this time.  
- NOTE: You may set only two IPs per ISP at this time.  
- The script is intended to work with two ISPs, making it automatically work with N ISPs is on the TODO list.
- You'll need to ensure the IPs you assign to your second ISP are static routed to use that ISP, I expect you already know how to do this with your route.  
- Run the container: `docker run -v '/path/to/isp-outage-tracker.conf:/app/isp-outage-tracker.conf:z' --name isptracker hardenrm/isptracker`
- Check the logs for proper operation: `docker logs -f isptracker`

Docker Compose:
- Copy the `docker-compose.yml` file to your docker host. Make sure to edit the path for `isp-outage-tracker.conf` to match your system.
- `docker-compose up -d`
- `docker logs -f isptracker` to ensure it started up with the correct settings.

#### InfluxDB
I assume you already have this set up. The user you set in the .conf file will need to have appropriate permissions.
The database name is configurable, but the retention policy is set to `awesome_policy`. I can't explain why.

#### Grafana
- Create a datasource that defaults to use the database name you set in the conf file.
- Copy the contents of the `sample-dashboard.json` file and import it into your Grafana install.
- You may need to tweak things slightly as I haven't set up the dashboard to be very dynamic.


#### TODO
- Dynamically detect number of ISPs
- Dynamically detect number of IPs per ISP
- Create a more dynamic Grafana Dashboard