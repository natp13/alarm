import socket

ipaddr = "192.168.1.105"

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80)) # this is apparently some google server?
    ipaddr = s.getsockname()[0]
    s.close()
    print "Current ip address: " + ipaddr
except:
    # if there is an error, just use the default ip address
    print "Error acquiring ip address"
    pass

file = open("/home/pi/alarm/site2.html", "r")
siteV2 = file.read()
siteV2 = siteV2.replace("#REPLACE_WITH_IP_ADDRESS#", ipaddr, 1) #(replace the first occurence only)
file.close()
