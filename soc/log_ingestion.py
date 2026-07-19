
import re
from database.db import insertAlert

def parseAuthLog(filepath):
    """
    Reads auth.log line by line and extracts failed login attempts.
    Uses regex to extract IP and username since log format has no consistent delimiters.
    Saves each finding to database as an alert.
    """
    with open(filepath, 'r') as f:
        for line in f:
            if "Failed password" in line:
                sourceIP = None
                username = None
                
                sourceIP = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                username = re.search(r'for (\w+) from', line)

                if sourceIP:
                    sourceIP = sourceIP.group(1)

                if username:
                    username = username.group(1)

                insertAlert(sourceIP, 'failed_login', f'Failed password attempt for {username}')
                print(f"[ALERT] Failed login — IP: {sourceIP} | User: {username}")


#Note when you write re.search, this just returns match object, you just need to unpack with key so do .group(1)