from scapy.all import sniff, IP, TCP, UDP
import time
from database.db import insertPacket, insertAlert
from capture.anomaly import logConnection

# we added this line after creating dashboard this is because right now the sniffer just stores inside list packetLog, which will be lost due to limited memory so we import database so database functions can save data permanentely

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
        
        entry = {  #here we create an entry based on the data packets that we have captured passing though, before appending it to a "list" of captured packets
            "time": timestamp,
            "src": sourceIP,
            "dst": destIP,
            "protocol": protocol,
            "size": size
        }
        packetLog.append(entry)  #the packets passed through we captured will be added into the entry

        insertPacket(timestamp, sourceIP, destIP, protocol, size)
        #added this so that every packet that passes through the processPacket will get saves instantly to database, 
        #and THIS, when saved to database will show the breakdown of the protocol dashboard with real data

        
        if logConnection(sourceIP):
            insertAlert(sourceIP, 'brute_force', 'Exceeded connection threshold')
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

