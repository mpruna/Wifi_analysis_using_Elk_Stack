### Wifi analysis using airckrack-ng and elasticsearch


A while back I was interested in security, it seemed at that point a sexy domain and let's be fair there's something special about being a hacker or at least in Hollywood there is some romantic portrayal of hackers.
At that time I began experimenting with Kali Linux, and it's adjacent software, and I ended up getting a Wireless Penetration testing certification from Offensive Security.
Now it's time to put my knowledge into practice and do an analysis of the wifi access point in my City using aircrack-ng and Elasticsearch.

Kali Linux is a  Debian based distribution that with software used mainly in penetration testing.
For example, Kali has specialized software for:

    * Information Gathering
    * Vulnerability Assesment
    * Web Application Analysis
    * Wireless attacks 
    

Kali version:

```
4.18.0-kali2-amd64
```

Exploit workflow:
    * scanning (in this phase we get as much useful information as possible on the target)
    * vulnerability assessment(check out which would be the best way to get access on the target)
    * get access
    * elevate privileges
    * exploit

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/exploit_work_flow.png)
    
In this tutorial, I'm not going to do any exploitation/anything illegal. Instead, I would like to focus on the analysis part.
On any given set up the dataset, the analysis is a prerequisite, for formulating a valid hypothesis and providing answers.
After data cleanup(removal, wrangle missing data, feature engineering), data analysis is vital. Next logical step would be to choose a proper modeling algorithm and provide some answers based on that model.


Wardriving is the act of searching for Wi-Fi wireless networks by a person usually in a moving vehicle, using a laptop or smartphone. Software for wardriving is freely available on the [Link](https://en.wikipedia.org/wiki/Wardriving)
For this, we use [aircrack-ng]('https://www.aircrack-ng.org/'), a complete suite of tools to assess WiFi network security capable of:

    * Monitoring: Packet capture and export of data to text files for further processing by third-party tools
    * Attacking: Replay attacks, deauthentication, fake access points, and others via packet injection
    * Testing: Checking WiFi cards and driver capabilities (capture and injection)
    * Cracking: WEP and WPA PSK (WPA 1 and 2)
    
### This is a two-stage process:

   1. Start interface in monitor mode. We will use a USB antenna with better performance:
    
    ```
    Bus 001 Device 005: ID 148f:3070 Ralink Technology, Corp. RT2870/RT3070 Wireless Adapter
    ip addr | grep wlan0
    3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    inet 192.168.1.12/24 brd 192.168.1.255 scope global dynamic noprefixroute wlan0
    ```
    
    ```
    airmon-ng start wlan0
    
    Found 3 processes that could cause trouble.
    Kill them using 'airmon-ng check kill' before putting
    the card in monitor mode, they will interfere by changing channels
    and sometimes putting the interface back in managed mode

      PID Name
      586 NetworkManager
      668 wpa_supplicant
      913 dhclient

    PHY Interface    Driver    Chipset

    phy0   wlan0   ath10k_pci  Qualcomm Atheros QCA6174 802.11ac Wireless Network Adapter (rev 20)

        (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
        (mac80211 station mode vif disabled for [phy0]wlan0)
    phy    1wlan   1rt2800usb   Ralink Technology, Corp. RT2870/RT3070
    ```
    
   2. Capture wifi trafic
   
   ```
     airodump-ng wlan0mon -w elastic_wd
   
     CH 13 ][ Elapsed: 12 s ][ 2018-11-21 05:25                                         
                                                                                                                                                                                                                  
     BSSID              PWR  Beacons    #Data, #/s  CH  MB   ENC  CIPHER AUTH ESSID
                                                                                                                                                                                                                  
                                                                                                                       
     86:25:19:2F:70:87  -72        6        0    0   6   65  WPA2 CCMP   PSK  DIRECT-25C48x Series                                                                                                                    
     04:8D:38:7E:C4:40  -76       27       16    2   9  270  WPA2 CCMP   PSK  Netis 12                                                                                                                                
     D8:EB:97:15:BC:A9  -77       17        1    0  12  130  WPA2 CCMP   PSK  trendnet                                                                                                                                
     04:8D:38:0B:CE:64  -77       20        0    0   2  135  WPA2 CCMP   PSK  netis                                                                                                                                   
     10:7B:44:AC:93:40  -79       16        1    0  13  260  WPA2 CCMP   PSK  ASUS 2.4                                                                                                                                
     F8:D1:11:8D:F3:DA  -79       12        0    0   1  54e. WPA2 CCMP   PSK  Nu exista semnal!                                                                                                                       
         
    -rw-r--r-- 1 root root  2416 Nov 21 05:25 elastic_wd-01.csv
    -rw-r--r-- 1 root root 23245 Nov 21 05:25 elastic_wd-01.kismet.netxml
    -rw-r--r-- 1 root root  3508 Nov 21 05:25 elastic_wd-01.kismet.csv
    -rw-r--r-- 1 root root 18280 Nov 21 05:25 elastic_wd-01.cap
    -rw-r--r-- 1 root root 11650 Nov 21 05:28 elastic_wd-02.kismet.netxml
    -rw-r--r-- 1 root root   848 Nov 21 05:28 elastic_wd-02.kismet.csv
    -rw-r--r-- 1 root root  1244 Nov 21 05:28 elastic_wd-02.csv
    -rw-r--r-- 1 root root  4081 Nov 21 05:28 elastic_wd-02.cap
   ```

### Install elasticsearch

Elasticsearch is a Java application, so you'll need to install a recent version OpenJDK.

```
apt-get install default-jdk
```

Add elasticsearch key and install version 6

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" |  tee -a /etc/apt/sources.list.d/elastic-6.x.list
apt-get update &&  apt-get install elasticsearch
```

### Post installation adjustments

We need to edit elasticsearch config file so we can access it from the host, which means we need to allow HTTP traffic on port 9200.

```
nano /etc/elasticsearch/elasticsearch.yml
Change network.host to 0.0.0.0 and host.http: 9200
```

Elasticsearch stores it's data into inverted indexes distributed across many shards. A shard holds just a subset of the `dataset.`
By default, `Elastic` uses 5 shards and 1 replica, and this means that for every shard there is a `backup,` and we don't need this.
As this is not a production environment and we want to demonstrate the functionality we setup `1 shard` and `0 replicas`.

!['Img'](https://github.com/mpruna/IMPORTING_DATA_INTO_ELASTICSEARCH/blob/master/images/inverted_index.png)

There is not a distributed system and we have only 1 node. Also by default `elastic` stores it's data on `/var/lib` partition and tipically that parition is small. We specify media path in the `/home` directory.

```
#action.destructive_requires_name: true
#Shards
index.number_of_shards: 1
index.number_of_replicas: 0

#Node setup
node.data: false

#Sepcify a different data path:
path.data: /home/media/
```

Starting with Elasticsearch -v6 `Content-Type` header is required in `REST-API` requests. Instead of specifying this implicitly every time we interact with elasticsearch using `curl,` we set up a script which makes this behavior default. 
We also need to make it part of the system variables, so it's persistent across reboots:

```
mkdir bin
cd bin
#!/bin/bash
/home/bin/curl  -s -H "Content-Type: application/json" "$@"
chmod a+x curl
```
Export `curl` to enviroment `PATH`

```
export PATH=:"/home/bin/:$PATH"
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

### Import data into Elasticsearch using python

Elasticsearch has ['client libraries'](https://www.elastic.co/guide/en/elasticsearch/client/index.html) available for below languages:
    
    * Java API
    * JavaScript API
    * Groovy API 
    * .NET API
    * PHP API
    * Perl API
    * Python API
    * Ruby API

First we install Python package manager `pip` then using `pip` we install `elasticsearch-python` client.

```
apt-get install python3-pip
pip3 install elasticsearch
```

With the script below we import wifi data into elasticsearch:

```
import csv
from collections import deque
import elasticsearch
from elasticsearch import helpers

# Above imported necessary python moduels

# Function below converts a .csv file into json 

def json_converter():
    with open("elastic_wardrive-01.kismet.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        next(csv_reader)
        for line in csv_reader:
            wifi = {}
            wifi['Network'] = int(line[0])
            wifi['NetType'] = str(line[1])
            wifi['ESSID'] = str(line[2])
            wifi['BSSID'] = str(line[3])
            wifi['Channel'] = int(line[5])
            wifi['Encryption'] = str(line[7])
            wifi['MaxRate'] = float(line[9])
            yield wifi

# bulk import into elasticsearch
es = elasticsearch.Elasticsearch()
es.indices.delete(index="wifis",ignore=404)
deque(helpers.parallel_bulk(es,json_converter(),index="wifis",doc_type="wifi",chunk_size=350),maxlen=0)
es.indices.refresh()
```

#### Importing and validate import

```
python3 convert_csv_to_json.py
curl -XGET 127.0.0.1:9200/_cat/indices?pretty
green  open .kibana_1 OwOU0o4cTU-taduRA5b_og 1 0    4 0  20.6kb  20.6kb
yellow open wardrive  CGLIdGQXQNCpMr1FB-CIIw 5 1 5075 0 980.2kb 980.2kb
```

Check the number of records imported:

```
curl -XGET 127.0.0.1:9200/wardrive/_count?pretty
{
  "count" : 5075,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  }
}
```

At the moment there are 5075 records and let's check how an individual record looks like:
```
curl -XGET '127.0.0.1:9200/wardrive/wifi/_search?size=1&pretty'
{
  "took" : 20,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : 5075,
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "wardrive",
        "_type" : "wifi",
        "_id" : "NZr-T2cBJGzqhtzfIGxH",
        "_score" : 1.0,
        "_source" : {
          "Network" : 4,
          "NetType" : "infrastructure",
          "ESSID" : "Netis 14 Spalatorie",
          "BSSID" : "04:8D:38:7E:C4:37",
          "Channel" : 9,
          "Encryption" : "WPA2,AES-CCM,TKIP",
          "MaxRate" : 270.0
        }
      }
    ]
  }
}
```

Index explanation

Column | Description
-|-
Channel | Channel number (taken from beacon packets).
ESSID |  Shows the wireless network name. The so-called “SSID”, which can be empty if SSID hiding is activated
Encryption | Encryption algorithm in use. OPN = no encryption,“WEP?” = WEP or higher (not enough data to choose between WEP and WPA/WPA2), WEP (without the question mark) indicates static or dynamic WEP, and WPA or WPA2 if TKIP or CCMP is present.
BSSID | MAC address of an Access Point


Check the number of access points with `NO Encription`/`WEP`/`WPA`

NO Encryption

```
curl -XGET 127.0.0.1:9200/wardrive/wifi/_count?pretty -d'
{
"query":{
"match":{
"Encryption":"OPN,None"
}
}
}'
{
  "count" : 206,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  }
}
```

WPA2

```
curl -XGET 127.0.0.1:9200/wardrive/wifi/_count?pretty -d'
{
"query":{
"match":{
"Encryption":"WPA2"
}
}
}'
{
  "count" : 4744,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  }
}

```

WEP

curl -XGET 127.0.0.1:9200/wardrive/wifi/_count?pretty -d'

```
{
"query":{
"match":{
"Encryption":"WEP"
}
}
}'
{
  "count" : 27,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "skipped" : 0,
    "failed" : 0
  }
}
```


### Install Kibana

[Kibana]('https://www.elastic.co/products/kibana') it's elasticsearch Web UI. 
Working with the `linux` shell might not be the best thing for a nont technical individuals. A lot of the times you need to provide the same information for other staff/company members and this is why we will install it. Kibana provides enhanced visualization capabilities as as an API builder.


```
apt-get update && apt-get install kibana
```

Setup http access:
```
server.port: 5601
server.host : 0.0.0.0
```

Allow http host access:

```
VBoxManage modifyvm "Elastic_Stack" --natpf1 "host2guest-kibana_http,tcp,,5601,,5601"
```

Setup and deamonize Kibana service:

```
/bin/systemctl daemon-reload
/bin/systemctl enable kibana.service
/bin/systemctl start kibana.service
```

Let's check if we can access Kibana UI by accessing our localhot:5601 in the web brawser.

[Img]('https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/Kibana_UI.png')

Bar chart

[Img]('https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/bar_chart.png')

Pie chart

[Img]('https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/Encyption_pie.png')
