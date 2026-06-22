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



    if attemptCount >= MAX_CONNECTIONS:
        print(f"[ALERT] Possible brute force from {sourceIP} — {attemptCount} connections in {TIME_WINDOW}s")
        return True

    return False
