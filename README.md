### Wifi analysis using airckrack-ng and elasticsearch


A while back I was interested in security. There is something special about being a hacker, something mysterious, something that captures our imagination, and even in Hollywood, there are a lot of movies centered around security related topics. It has that "it factor," and I ended up getting a Wireless Penetration testing certification from Offensive Security:`OS-BWA-02622`. Now it's time to put my knowledge into practice and do an analysis of the WiFi access point in my City using aircrack-ng and elasticsearch.

Kali Linux is a Debian based distribution used mainly in penetration testing. For example, Kali has specialized software for:
* Information Gathering
* Vulnerability Assessment
* Web Application Analysis
* Wireless attacks
* Web Application Exploit
* Database Exploit


Kali version:

```
4.18.0-kali2-amd64
```

Exploit workflow:

    Scanning (in this phase we get as much useful information as possible on the target)
    vulnerability Assessment(check out which would be the best way to gain access to the host)
    Get Access
    Elevate Privileges
    Exploit

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/exploit_work_flow.png)

In this tutorial, we perform a quantitative access point analysis using Python, Elasticsearch, and `aircrack-ng`.

Workflow:

    Gather the data
    Wrangle the data, if needed
    Upload the data into elasticsearch
    Analyze the data


### Gathering WiFi data

The term coined for this specific action is `wardriving.`
`Wardriving` is the act of searching for WiFI wireless networks by a person usually in a moving vehicle, using a laptop or smartphone.
I'm using an `Alfa Networks` wireless antenna. When in monitor mode this antenna is sending probe requests to nearby access points. The access-points reply to these request with its capabilities, i.e., `ESSID,` `Encryption,` `Channel.`


!['IMG'](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/probe_request_response.png)

Software used for wardriving is freely available [here](https://en.wikipedia.org/wiki/Wardriving).
We use [aircrack-ng]('https://www.aircrack-ng.org/'), a complete suite of tools capable of assessing WiFi network security.

`aircrack-ng`  capabilities:

    * Monitoring: Packet capture and export of data to text files for further processing by third-party tools
    * Attacking: Replay attacks, deauthentication, fake access points, and others via packet injection
    * Testing: Checking WiFi cards and driver capabilities (capture and injection)
    * Cracking: WEP and WPA PSK (WPA 1 and 2)


1. Put wlan0 in monitor mode: `arimon-ng start wlan0`

```
Bus 001 Device 005: ID 148f:3070 Ralink Technology, Corp. RT2870/RT3070 Wireless Adapter
ip addr | grep wlan0
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
inet 192.168.1.12/24 brd 192.168.1.255 scope global dynamic noprefixroute wlan0


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

2. Capture WiFi traffic:`airodump-ng wlan0mon -w elastic_wd`, `-w` specifies where to write the file.

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

### Install `elasticsearch`

What is `elasticsearch`? `Elasticsearch` is a distributed, RESTful search and analytics engine capable of solving a growing number of use cases. More information [here](https://www.elastic.co/products/elasticsearch) or on my [github_repo](https://github.com/mpruna/IMPORTING_DATA_INTO_elasticsearch).
`Elasticsearch` stores it's data into inverted indexes distributed across many shards. A shard holds just a subset of the `data.`
By default, `Elastic` uses 5 shards and 1 replica, and this means that for every shard there is a `backup.`
`Elasticsearch` structure differs from a traditional SQL database, but for those familiar with `SQL` we can use below analogy:

SQL | elasticsearch
-|-  
Databases  | Indices  
Tables  | Types  
Rows  | Documents  
Column  | Fields  

!['Img'](https://github.com/mpruna/IMPORTING_DATA_INTO_elasticsearch/blob/master/images/inverted_index.png)


`Elasticsearch` is a Java application, so we need to install a recent version OpenJDK.

```
apt-get install default-jdk
```

`apt-key` is used to manage the list of keys used by apt to authenticate packages. `Elastisearch` must be authenticated with a key, add elastic source to our package manager, then we install -version 6.

```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" |  tee -a /etc/apt/sources.list.d/elastic-6.x.list
apt-get update &&  apt-get install elasticsearch
```

### Post installation adjustments

Allow HTTP host access to `elasticsearch` on port 9200.

```
nano /etc/elasticsearch/elasticsearch.yml
Change network.host to 0.0.0.0 and host.http: 9200
```

Starting with `elasticsearch` -v6 `Content-Type` header is required in `REST-API` requests. Instead of specifying this implicitly every time we interact with `elasticsearch` using `curl,` we set up a script which makes this behavior default.
We make the `curl` script folder location part of the system variables.

Curl script:
```
mkdir bin
cd bin
#!/bin/bash
/home/bin/curl  -s -H "Content-Type: application/json" "$@"
chmod a+x curl
```
Export `curl` to environment `PATH` and also make the `curl` script part of `.bashrc,` `.profile` files so it will be persistent across reboots.

```
export PATH=:"/home/bin/:$PATH"
echo $PATH
/home/bin/:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
echo "export PATH="/home/bin/:$PATH"" >.bashrc
echo "export PATH="/home/bin/:$PATH"" >.profile
```

### Import data into `elasticsearch` using python

`elasticsearch` has ['client_apis'](https://www.elastic.co/guide/en/elasticsearch/client/index.html) available for below languages:

    * Java API
    * JavaScript API
    * Groovy API
    * .NET API
    * PHP API
    * Perl API
    * Python API
    * Ruby API


Since we use python programming language for data import, it's a good idea to install python native package manager `pip.` After this using `pip` we install `python-elsticsearch` client.

```
apt-get install python3-pip
pip3 install elasticsearch
```
#### Import and validat import

With `elastic_import.ipynb`  notebook we do a preliminary analysis, and then we import data into `elasticsearch.`

Section below

```
es = Elasticsearch(["127.0.0.1:9200"])

es.indices.delete(index="wardrive",ignore=404)
docs = df_short.to_dict(orient='records')
bulk(es, docs, index='wardrive',doc_type='wifi', raise_on_error=True)
es.indices.refresh()
```

Check index is created:

```
curl -XGET 127.0.0.1:9200/_cat/indices?pretty
green  open .kibana_1 OwOU0o4cTU-taduRA5b_og 1 0    4 0  20.6kb  20.6kb
yellow open wardrive  CGLIdGQXQNCpMr1FB-CIIw 5 1 5075 0 980.2kb 980.2kb
```

Determine the number of records:

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

Check how an individual record looks like. We could look at the first record by specifying `size=1` parameter in our query.

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
MaxRate  |  Rate: AP/client transmission speeds; MaxRate is the best transmission seen
NetType  |  infrastructure mode are generally created by Wi-Fi routers, while ad-hoc networks are usually short-lived networks created by a laptop or other device
Channel | Channel number (taken from beacon packets).
ESSID |  Shows the wireless network name. The so-called “SSID”, which can be empty if SSID hiding is activated
Encryption | Encryption algorithm in use. OPN = no encryption,“WEP?” = WEP or higher (not enough data to choose between WEP and WPA/WPA2), WEP (without the question mark) indicates static or dynamic WEP, and WPA or WPA2 if TKIP or CCMP is present.
BSSID | MAC address of an Access Point

[Channel_Wiki](https://en.wikipedia.org/wiki/List_of_WLAN_channels)
The 802.11 standard provides several distinct radio frequencies ranges for use in Wi-FI communications. Each channel has 22MHz around the central frequency.
![IMG](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/channel_distribution.png)

Check the number of access points with `NO Encription`/`WEP`/`WPA`

NO Encryption count:

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


WPA2 Encryption count:

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

WEP Encryption count:

```
curl -XGET 127.0.0.1:9200/wardrive/wifi/_count?pretty -d'

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
'
```



### Install Kibana

[Kibana]('https://www.elastic.co/products/kibana') it's `elasticsearch` Web UI.
Working with the `linux` shell might not be the best thing for a non technical individuals. A lot of the times you need to provide the same information for other staff/company members or in a presentation.Because people are visually inclined, and because `A picture's worth a thousand words` we will install it.
`Kibana` provides:
  - enhanced visualization capabilities (histograms, line graphs, bar charts pie charts)
  - API builder
  - Machine Learning modules
  - Log Analysis
  - Security via `X-PACK`


```
apt-get update && apt-get install kibana
```

Setup HTTP access:
```
server.port: 5601
server.host : 0.0.0.0
```

Allow HTTP host access:

```
VBoxManage modifyvm "Elastic_Stack" --natpf1 "host2guest-kibana_http,tcp,,5601,,5601"
```

Setup and demonize `Kibana` service:

```
/bin/systemctl daemon-reload
/bin/systemctl enable kibana.service
/bin/systemctl start kibana.service
```

Let's check if we can access `Kibana` UI by accessing our 127.0.0.1:5601 in the web browser.

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/kibana.png)

Bar chart creation: `Click Visualize`; `+ symbol`; `Vertical Bar`; `Select Index`; `from Buckets(X-Axis)`; `Select Terms`; `Select Field (Encryption.keyword)`; `Order by metric(count)`; `Size 10`

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/bar_chart.png)

Pie chart creation: `Click Visualize`; `+ symbol`; `Pie Chart`; `Select Index`; `from Buckets(Split Slices)`; `Select Terms`; `Select Field (Encryption.keyword)`; `Order by metric(count)`; `Size 10`

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/kibana_pie.png)

Tag cloud creation: `Click Visualize`; `+ symbol; Pie Chart`; `Select Index`; `from Buckets(Tags)`; `Select Terms`; `Select Field (Encryption.keyword)`; `Order by metric(count)`; `Size 10`

![Img](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/tag_cloud.png)


#### Dashboards:

We can create dashboards, but we need to tag the charts we cant to use. When we save visualization we are asked to give it a name. We can then use this name as a tag in the dashboard builder.

Dashboard creation: `Click Dashboard`; `Create new dashboard`;`Click Add`:`From add panel(Under title) add predefined visualization`;`Add`:`Save`

Dashboards

![IMG](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/dashboard.png)

![IMG](https://github.com/mpruna/Wifi_analysis_using_Elk_Stack/blob/master/images/dashboard2.png)


Resources:

  [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elk-stack-on-ubuntu-14-04)

  [Milan Gabor - Creative hackers way to use ELKstack](https://www.youtube.com/watch?v=eQTLKt6GgoA)

  [Elk for Hackers](https://www.viris.si/2016/01/elk-stack-for-hackers/?lang=en)

  [Elasticsearch official docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

  [Elasticsearch in depth and hands on](https://www.udemy.com/elasticsearch-6-and-elastic-stack-in-depth-and-hands-on/?couponCode=ELASTIC19)
