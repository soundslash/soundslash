import urllib2,random,re,socket
from netaddr import IPNetwork, IPAddress
from urlparse import urlparse

ip_regex = re.compile("(([0-9]{1,3}\.){3}[0-9]{1,3})")

hosts = """http://jsonip.com/
http://adresseip.com
http://www.ipchicken.com/
http://monip.net/
http://checkrealip.com/
http://ipcheck.rehbein.net/
http://checkmyip.com/
http://www.raffar.com/checkip/
http://www.lawrencegoetz.com/programs/ipinfo/
http://www.edpsciences.org/htbin/ipaddress
http://mwburden.com/cgi-bin/getipaddr
http://www.glowhost.com/support/your.ip.php
http://checkip.eurodyndns.org/""".strip().split("\n")

def public_ip():
    # return "192.168.3.119"
    # return "188.167.52.241"
    # return "192.168.0.2"
    ''' Returns your public IP address.
        Output: The IP address in string format.
                None if not internet connection available.
    '''
    ips = {}
    # List of host which return the public IP address:

    random.shuffle(hosts)

    for i in range(len(hosts)):
        host = hosts[i]
        try:
            results = ip_regex.findall(urllib2.urlopen(host, timeout=1).read(200000))
            ip = results[0][0]
            # 10.0.0.0 - 10.255.255.255
            # 172.16.0.0 - 172.31.255.255
            # 192.168.0.0 - 192.168.255.255
            if results:
                if IPAddress(ip) in IPNetwork("10.0.0.0/8") or IPAddress(ip) in IPNetwork("172.16.0.0/12") or IPAddress(ip) in IPNetwork("192.168.0.0/10"):
                    raise Exception
                if ip in ips:
                    ips[ip]+=1
                else:
                    ips[ip]=1
                    # 3 or more servers returned ip
                if ips[ip] >= 3:
                    print("Public IP: "+ip)
                    return ip
        except:
            pass # Let's try another host
    return None

def local_ip():
    # return "192.168.3.119"
    # return "192.168.0.2"
    # return "10.0.3.15"

    lhosts = ip4_addresses()

    for i in range(len(lhosts)):
        try:
            ip = lhosts[i]
            # print ip
            # 10.0.0.0 - 10.255.255.255
            # 172.16.0.0 - 172.31.255.255
            # 192.168.0.0 - 192.168.255.255
            if ip:
                if IPAddress(ip) in IPNetwork("10.0.0.0/8") or IPAddress(ip) in IPNetwork("172.16.0.0/12") or IPAddress(ip) in IPNetwork("192.168.0.0/10"):

                    print("Local IP: "+ip)
                    return ip
        except:
            pass # Let's try another host
    return None


from netifaces import interfaces, ifaddresses, AF_INET

def ip4_addresses():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface)[AF_INET]:
            ip_list.append(link['addr'])
    return ip_list
