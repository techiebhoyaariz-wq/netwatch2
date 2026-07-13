import socket
import time
import struct

def udp_client(server_ip, server_port, duration, interval, rate_kbps):
    """
    Sends UDP packets to server at controlled rate.
    Measures bandwidth per interval. Server measures packet loss and jitter.
    No ACK mode - server side does the measuring.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #we do this to create a socket/tunnel like where data can essentially flow between client and server

    packet_size = 1472 #this is to declare the size of packet needed
    bits = packet_size * 8 #convert to bits to figure out send interval
    send_rate_interval = bits / (rate_kbps * 1000) #seconds between each packet - controls the send rate

    payload_data = bytes([65]) * 1468 #dummy data converted to BYTES because sockets only speak bytes

    transmissionTime = time.time() #record the time of transmission when test started
    packet_id = 1 #sequence number - server detects gaps in sequence = packet loss
    next_send = transmissionTime #tracks when next packet should be sent
    lastReportTime = transmissionTime #tracks when we last reported stats
    byte_intervals = [] #bytes sent this interval - resets each report period to show current bandwidth

    while True:
        time_recorded = time.time() #this is the current time that we want

        #We subtract transmissionTime because without it loop breaks on first iteration
        #time_recorded - transmissionTime tells us HOW LONG the test has been running
        if time_recorded - transmissionTime >= duration: #stop test once duration reached
            break

        #Note we have two timers under one loop
        #Timer 1 - controls WHEN to send packets
        #Timer 2 - controls WHEN to report stats
        if time_recorded >= next_send: #only send if enough time passed since last packet
            header = struct.pack(">I", packet_id) #pack sequence number into 4 byte header
            packet = header + payload_data #join header and payload to create data packet
            sock.sendto(packet, (server_ip, server_port)) #send to server identified by IP and port
            packet_id = packet_id + 1 #increment sequence number for next packet
            next_send += send_rate_interval #schedule when next packet should be sent
            size = len(packet)
            byte_intervals.append(size) #record bytes sent this iteration

        timeTaken = time_recorded - lastReportTime
        if timeTaken >= interval: #time to report the stats
            intervalBytes = sum(byte_intervals) #total bytes sent this interval
            intervalBandwidth = (intervalBytes * 8) / (timeTaken * 1000000) #convert to Mbps
            print(f"Sent {packet_id - 1} packets | Bandwidth: {intervalBandwidth:.2f} Mbps")
            byte_intervals = [] #reset for next interval - we measure per interval not cumulative
            lastReportTime = time_recorded #clock restarted - wait interval seconds before reporting again

    #Server sits waiting indefinitely - it does not know test is over unless we inform it
    #So we send termination packet with sequence number 0 to signal test complete
    termination_header = struct.pack(">I", 0)
    termination_packet = termination_header + payload_data
    sock.sendto(termination_packet, (server_ip, server_port))

    print(f"Test complete. Sent {packet_id - 1} packets.")
    #packet_id - 1 because packet_id increments BEFORE sending stops
    #like a ticket machine - ticket 11 pulled but only 10 people served
    sock.close()


#NOW we need to go ahead and build the Server Side of the UDP


def udp_server(port, interval):
    """
    Listens for incoming UDP packets from clients.
    Tracks each client separately using their IP and port.
    Calculates bandwidth and packet loss per interval.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(("0.0.0.0", port))


    packetsReceived = {} #dictionary to track state of each connected client separately


    print(f"UDP server listening on port {port}")


    while True:
        data, address = sock.recvfrom(2048) #receive packet, get data and client IP Address
        pkt_id = struct.unpack(">I", data[0:4])[0] #extract sequence number from first 4 bytes to calculate packet loss
        currentTime = time.time()
        client_ip, client_port = address #parse IP and PORT from address tuple for printing stats

        #termination marker - pkt_id 0 means client finished sending, time to show final stats
        if pkt_id == 0:
            if address in packetsReceived:
                info = packetsReceived[address]
                packets_sent = info["lastIDHighest"] - info["interval_start_id"] #highest ID minus start ID = how many should have arrived
                if packets_sent > 0:
                    percentage_lost = ((packets_sent - info["interval_received"]) / packets_sent) * 100
                    print(f"[FINAL] {client_ip}:{client_port} | Loss: {percentage_lost:.2f}%")
                del packetsReceived[address] #clear client from dictionary once done
            break

        #first time we see this client - initialise their tracking dictionary
        if address not in packetsReceived:
            packetsReceived[address] = {
                "lastIDHighest": pkt_id, #cannot use False - need actual ID for integer comparison
                "interval_bytes": 0,
                "interval_received": 0,
                "interval_start_time": currentTime,
                "interval_start_id": pkt_id #start from actual first packet not 0 - avoids false loss reading
            }

        #update this client's stats every packet that arrives
        
        info = packetsReceived[address]
        info["interval_bytes"] += 1472 #fixed size not len(data) - measures expected not actual for consistency

        info["interval_received"] += 1 #count packets received this interval

        if pkt_id > info["lastIDHighest"]: #only update if higher - packets can arrive out of order
            info["lastIDHighest"] = pkt_id

        #report stats every interval seconds - two timers in one loop
        elapsed = currentTime - info["interval_start_time"]
        if elapsed >= interval:
            bandwidth = (info["interval_bytes"] * 8) / (elapsed * 1000000) #convert bytes to Mbps
            packets_sent = info["lastIDHighest"] - info["interval_start_id"]
            percentage_lost = ((packets_sent - info["interval_received"]) / packets_sent) * 100 if packets_sent > 0 else 0

            print(f"[{client_ip}:{client_port}] Bandwidth: {bandwidth:.2f} Mbps | Loss: {percentage_lost:.2f}%")
            #reset interval counters for next reporting period - measure current not cumulative
            
            info["interval_bytes"] = 0
            info["interval_received"] = 0
            info["interval_start_time"] = currentTime
            info["interval_start_id"] = info["lastIDHighest"] #start next interval from where we left off