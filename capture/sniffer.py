from scapy.all import sniff, IP, TCP, UDP
import time
from soc.ioc_tracker import checkIOC
from capture.anomaly import logConnection, detectPortScan
from database.db import insertPacket, insertAlert

# tracks packets captured per source IP; essentially what we do it maintain a list of ALL packets we captured
packetLog = []

def processPacket(packet):
    """This function gets called automatically by Scapy for every packet we captured"""
    if IP in packet:
        sourceIP = packet[IP].src
        destIP = packet[IP].dst
        protocol = "TCP" if TCP in packet else "UDP" if UDP in packet else "OTHER" #most common are UDP/TCP
        size = len(packet)
        timestamp = time.strftime('%H:%M:%S')

        #Note we moved both if statements up here because this is all in line related to the types of protocol detected obviously. Logically should have realised this but why didnt I
        
        entry = {  #here we create an entry based on the data packets that we have captured passing though, before appending it to a "list" of captured packets
            "time": timestamp,
            "src": sourceIP,
            "dst": destIP,
            "protocol": protocol,
            "size": size
        }
        packetLog.append(entry)  #the packets passed through we captured will be added into the entry

        insertPacket(timestamp, sourceIP, destIP, protocol, size) #REMEMBER the parameters need right order in way declared
        #Note when importing and reusing diferent functions in code and adding parameters, they need to be in same order they been declard before!

        if logConnection(sourceIP):  #Why do we use this IP only?
            insertAlert(sourceIP, 'brute_force', f'Brute force detected — {sourceIP} exceeded connection threshold', 'HIGH')
            #Remember the parameters like details and type like declared in other file are like parameters replaced they we place depending on context of the file

        #added this function here cause checkIOC exists but nothing ever calls it during live traffic
        #so every time packet flows/captured we check against watchlist to see if malicioius or not

        if checkIOC(sourceIP):
            insertAlert(sourceIP, 'ioc_match', f'Known malicious IP detected in live traffic — {sourceIP}', 'CRITICAL')

        if TCP in packet:
            destPort = packet[TCP].dport
            if detectPortScan(sourceIP, destPort):
                insertAlert(sourceIP, 'port_scan', f'TCP scan — contacted port {destPort}', 'MEDIUM')

        if UDP in packet:
            destPort = packet[UDP].dport
            if detectPortScan(sourceIP, destPort):
                insertAlert(sourceIP, 'port_scan', f'UDP scan — contacted port {destPort}', 'MEDIUM')

        print(f"[{timestamp}] {protocol} {sourceIP} → {destIP} ({size} bytes)")

def startSniffing(interface="lo", duration=30):
    """
    Captures live packets on the given interface for set duration.
    lo = loopback interface (localhost traffic on Linux)
    """
    print(f"Starting packet capture on {interface} for {duration} seconds...")
    sniff(iface=interface, prn=processPacket, timeout=duration, store=False)
    print(f"Capture complete. {len(packetLog)} packets logged.")
    return packetLog
