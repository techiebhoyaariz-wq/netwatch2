import requests
import json

def sendDiscordAlert(source_ip, alert_type, details):
    webhook_url = "https://discord.com/api/webhooks/FAKE/FAKE"
    message = {"content": f"[ALERT] {alert_type} | IP: {source_ip} | {details}"}


    response = requests.post(webhook_url, json=message) #here we send the data, converted as json via POST request


    if(response.status_code == 200):
         print("Successfully sent it over")
