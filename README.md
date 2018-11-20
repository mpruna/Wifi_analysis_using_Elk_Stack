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

[Img]()
    
In this tutorial, I'm not going to do any exploitation/anything illegal. Instead, I would like to focus on the analysis part.
On any given set up the dataset, the analysis is a prerequisite, for formulating a valid hypothesis and providing answers.
After data cleanup(removal, wrangle missing data, feature engineering), data analysis is vital. Next logical step would be to choose a proper modeling algorithm and provide some answers based on that model.


Wardriving is the act of searching for Wi-Fi wireless networks by a person usually in a moving vehicle, using a laptop or smartphone. Software for wardriving is freely available on the Internet.[Ref](https://en.wikipedia.org/wiki/Wardriving)
For this we will use the aircrack-ng.
[Aircrack-ng]('https://www.aircrack-ng.org/') is a complete suite of tools to assess WiFi network security capable of:

    * Monitoring: Packet capture and export of data to text files for further processing by third party tools
    * Attacking: Replay attacks, deauthentication, fake access points and others via packet injectio
    * Testing: Checking WiFi cards and driver capabilities (capture and injection)
    * Cracking: WEP and WPA PSK (WPA 1 and 2)

