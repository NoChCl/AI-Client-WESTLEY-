import socket
import requests
import json
from base64 import b64encode

#highly recomended that you have NGINX, makes you a little more secure
#This is all example config - nearly identical to mine - below is a list of variables you need to fill out for your specific use case
#USERNAME, PASSWORD, PC_IP, PUBLIC_IP, PORT

USERNAME = "username"
PASSWORD = "password"

# Create the Authorization header
auth_str = f"{USERNAME}:{PASSWORD}"
auth_bytes = auth_str.encode("utf-8")
auth_b64 = b64encode(auth_bytes).decode("utf-8")
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Content-Type": "application/json"
}


def getLocalIp():
    """Get this device's local IP address on the current network."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable — just used to get routing info
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()

def determineOllamaUrl():
    # Get current local IP
    localIp = getLocalIp()

    # Define known addresses
    PC_IP = "192.168.0.0"               # Device running WESTLEY
    PUBLIC_IP = "123.45.67.89"          # Your server's public IP
    PORT = 1234                        # Port server is listening on
    
    # Decide based on current local IP
    if localIp == PC_IP:
        # You're on the PC itself
        url = f"http://127.0.0.1:{PORT}"
    elif localIp.startswith("192.168.0."):
        # You're in your server's network
        url = f"http://{PC_IP}:{PORT}"
    else:
        # You're accessing from outside
        url = f"http://{PUBLIC_IP}:{PORT}"
    
    url +="/process"
    
    
    return url
def sendPayload(payload, streamOutput=False):
    # Send the request
    #If you are not using auth/nginx, remove the headers flag
    try:
        response = requests.post(determineOllamaUrl(), headers=headers, json=payload, stream=streamOutput)
    except requests.exceptions.RequestException as e:
        print("Network error:", e)
        return None
        
    # Print the output
    if response.ok:
        return response
    else:
        print("Error:", response.status_code, response.text)
        return None

# Use this URL for all outbound requests
OLLAMA_URL = determineOllamaUrl()
print("WESTLEY target URL:", OLLAMA_URL)
