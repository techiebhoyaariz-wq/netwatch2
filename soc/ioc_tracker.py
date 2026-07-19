from database.db import insertAlert

maliciousIP = {"192.168.1.1", "10.0.0.1", "172.16.0.1", "192.168.1.1"}


def checkIOC(sourceIP):

    if sourceIP in maliciousIP:
        insertAlert(sourceIP, 'ioc match found', f'Known malicious IP detected, {sourceIP} is on IOC WatchList')
        print(f"[CRITICAL] IOC match — {sourceIP} is a known malicious IP")
        return True
    else:
        return False