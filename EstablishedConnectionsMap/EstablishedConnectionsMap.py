import subprocess, shlex, re, requests
import multiprocessing
from joblib import Parallel, delayed
import pandas as pd
from time import sleep
import matplotlib.pyplot as plt
import geopandas as gpd

def get_IP():
    ip_list = []
    cmd = subprocess.Popen(shlex.split("ss -tupn state established"), stdout=subprocess.PIPE)
    cmd = subprocess.check_output(shlex.split("awk '{print $5, $6}'"), stdin=cmd.stdout)
    output = cmd.decode("utf-8")
    output = output.split("\n")[1:-1] # removes 1st and last lines of output (both of which have useless output)
    # Unclean splitting of IP, PORT, PID and FD for nested listing 
    # IP: 159.89.102.xxx is removed to avoid logging connection to geolocation-db.com 
    output = [i.split(":") for i in output if "127.0.0.1" not in i and "192.168." not in i and "159.89.102." not in i]
    # Cleans PORT AND PID data and appends array of unique ip data (ie [IP, PORT, PID, FD]) into ip_list
    for i in output:
        ip = i[0]
        port = i[1].split(" ")[0]
        # Attempts to recover PID and FD for ESTABLISHED connection.
        try:
            pid = re.findall(r'pid=(.*?),', i[2])[0]
            fd = re.findall(r'fd=(.*?)\)', i[2])[0]
            ip_list.append([ip, port, pid, fd])
        except:
            ip_list.append([ip, port, "NONE", "NONE"])
    return ip_list
data = get_IP()


def get_Location(ip):
    # ip_list = [i[0] for i in ip_list]
    url = "https://geolocation-db.com/json/"+str(ip)+"&position=true"
    url = requests.get(url).json()

    if url["latitude"] != "Not found":
        location = [ip, url['country_name'], url['city'], url['latitude'], url['longitude']]
        return location

def get_PID_info(PID):
    cmd = subprocess.Popen(shlex.split("ps " + str(PID)), stdout=subprocess.PIPE)
    cmd = subprocess.check_output(shlex.split("awk '{print $5, $6, $7, $8}'"), stdin = cmd.stdout)
    output = cmd.decode("utf-8")
    return output.split("\n")[1]

fig, ax = plt.subplots(figsize=(11, 5.5))

my_public_ip = requests.get("https://ident.me/").content.decode("utf-8")
my_location = get_Location(my_public_ip)
print(my_location)

while True:
    ax.cla()
    ## Get and update data points
    location_data = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(get_Location)(i[0]) for i in data)

    ip = [i[0] for i in location_data]
    country = [i[1] for i in location_data]
    city = [i[2] for i in location_data]
    latitude = [i[3] for i in location_data]
    longitude = [i[4] for i in location_data]
    pid = [i[2] for i in data]
    application_data = [get_PID_info(i) for i in pid]

    df = pd.DataFrame(data={"IP": ip, "COUNTRY":country, "CITY":city, "LATITUDE":latitude, "LONGITUDE":longitude, "PID":pid, "Application":application_data})
    df = df.sort_values(by="PID", ascending=1)
    print(df)

    ## Plot data points
    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    countries.plot(color="lightgrey", ax = ax)
    ax.scatter(df["LONGITUDE"], df["LATITUDE"])

    for i in range(len(latitude)):
        ax.plot([my_location[4], longitude[i]], [my_location[3], latitude[i]], color="blue")
    plt.pause(0.5)
    # sleep(5)
