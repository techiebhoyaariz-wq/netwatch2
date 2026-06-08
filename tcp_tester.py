#Three things to fix before you type this into the file:

#socket.AF_NET → should be socket.AF_INET (you missed the I)
#socket.SOCK_STREAM_ → remove the underscore at the end

#Missing colon after the def line
#totalBytes and last_report are used but never defined — you need to initialise them before the while loop
#The payload size 64345 — change to 65536 which is exactly 64KB, a clean standard size

#Also keep your variable names consistent — you have startTime in camelCase but then start_time with underscore inside the bandwidth line. Pick one style. Since your assignment used camelCase, stick with that throughout.
#Here's what to actually type into the file — this is yours with the bugs fixed:
#python


def tcp_client(server_ip, server_port, duration, interval):
    """
    Sends data to a server identified by IP address and port number.
    Records start and end time of transmission to calculate bandwidth.
    Reports stats at regular intervals defined by the interval parameter.
    """
    # NOTE: AF_INET means we are using IPv4 addresses
    # SOCK_STREAM means this is a TCP connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))

    # allocate a fixed chunk of data to send repeatedly
    payload = b'X' * 65536

    startTime = time.time()
    lastReportTime = startTime
    totalBytes = 0

    while True:
        # stop sending once duration has been reached
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




 def tcp_server(port) : 
     
     #This listen for incoming TCP client connections on the given port. Multiple clients are handled simulaneously (obvious for this process)
     #using the select.select() multiplexing. Whenever there is EMPTY data that is received: the connection is THEN closed

     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
     server_socket.bind(("0.0.0.0", port))
     server_socket.listen()

     readList = [server_socket]
     print(f"Server is listening on Port" {port}")

  

    while True:

        rlist, _, _ = select.select(readList, [], [])

        if server_socket in rlist: #returns a list of sockets that are READY: to connect to server
            client_socket, client_address = server_socket.accept() #two things returned: the actual PIPE to specific client and the ADDRESS of the client
            readList.append(client_socket) #Once a client has connected : the specific socket belonging TO them is added to the Watch List: to be WATCHED
            rlist.remove(server_socket)

        for client_socket in rlist:
            if client_socket is server_socket:
                continue

            data = client_socket.recv(1024)

            if len(data) == 0:
            printf(f"Client has disconnected")
                client_socket.close()
                readList.remove(client_socket)
                continue
 }
