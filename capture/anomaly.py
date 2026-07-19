import time




# stores connection attempts per IP address
connectionLog = {}

# detection thresholds
MAX_CONNECTIONS = 10   # max allowed connections from one IP
TIME_WINDOW = 10       # within this many seconds

def logConnection(sourceIP):
    """
    Records each connection attempt from a source IP.
    Triggers an alert if too many attempts detected in the time window.
    """
    currentTime = time.time()

    if sourceIP not in connectionLog:
        connectionLog[sourceIP] = []

    # add this attempt to the log for this IP
    connectionLog[sourceIP].append(currentTime)

    # remove attempts older than the time window
    recentAttempts = []
    for t in connectionLog[sourceIP]:
        if currentTime - t <= TIME_WINDOW:
            recentAttempts.append(t)

    connectionLog[sourceIP] = recentAttempts

    attemptCount = len(connectionLog[sourceIP])

    #We also needed to have a mechanism to be detecing and analysting the TYPE of Port Scans that he been carried out


    if attemptCount >= MAX_CONNECTIONS:
        print(f"[ALERT] Possible brute force from {sourceIP} — {attemptCount} connections in {TIME_WINDOW}s")
        return True

    return False




portScanLog = {}

MAX_UNIQUE_PORTS = 10

def detectPortScan(sourceIP, destPort):
    """
    Tracks unique ports contacted by each source IP.
    Alerts if one IP contacts too many different ports - indicates reconnaissance.
    """
    if sourceIP not in portScanLog:
        portScanLog[sourceIP] = set() #empty set - automatically prevents duplicate ports

    portScanLog[sourceIP].add(destPort) #add this port to the set for this IP

    if len(portScanLog[sourceIP]) >= MAX_UNIQUE_PORTS:
        print(f"[ALERT][PORT_SCAN] {sourceIP} contacted {len(portScanLog[sourceIP])} unique ports in under {MAX_UNIQUE_PORTS} port threshold — possible reconnaissance activity")
        portScanLog[sourceIP] = set() #reset so same IP can trigger again on new scan
        return True

    return False


    
























