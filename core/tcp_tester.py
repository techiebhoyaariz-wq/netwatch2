import socket
import time
import select

def tcp_client(server_ip, server_port, duration, interval):
    """
    Sends data to a server identified by IP address and port number.
    Records start and end time of transmission to calculate bandwidth.
    Reports stats at regular intervals defined by the interval parameter.
    """
    # AF_INET means IPv4, SOCK_STREAM means TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    # fixed 64KB payload sent repeatedly for consistent measurement
    payload = b'X' * 65536
    startTime = time.time()
    lastReportTime = startTime
    totalBytes = 0
    while True:
        if time.time() - startTime >= duration:
            break
        sock.sendall(payload)
        totalBytes += len(payload)
        now = time.time()
        if now - lastReportTime >= interval:
            bandwidth = (totalBytes * 8) / (now - startTime) / 1_000_000
            print(f"Bandwidth: {bandwidth:.2f} Mbps")
            lastReportTime = now
    sock.close()
    print("Test complete")




def tcp_server(port):
    """
    Listens for incoming TCP client connections on the given port.
    Handles multiple clients simultaneously using select multiplexing.
    Closes a client connection when empty data is received.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen()

    
    # readList holds all sockets select is watching
    readList = [server_socket]
    print(f"Server listening on port {port}")
    while True:
        rlist, _, _ = select.select(readList, [], [])
        # new client knocking - accept and add to watch list
        if server_socket in rlist:
            client_socket, client_address = server_socket.accept()
            readList.append(client_socket)
            print(f"Client connected: {client_address}")
            rlist.remove(server_socket)


        # check existing clients for data
        for client_socket in rlist:
            if client_socket is server_socket:
                continue
            
            data = client_socket.recv(65536)


            # empty data means client disconnected
            if len(data) == 0:
                print(f"Client disconnected")
                client_socket.close()
                readList.remove(client_socket)
                continue