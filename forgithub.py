import subprocess
import requests
import smtplib
from email.mime.text import MIMEText

# Configure email settings
sender_email = 'your_email@example.com'
sender_password = 'your_password'
smtp_server = 'smtp.example.com'
smtp_port = 587
recipient_email = 'recipient_email@example.com'

# Function to get the externally facing IP address of the router
def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
    except requests.exceptions.RequestException:
        pass
    return None

# Function to send an email notification
def send_email(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print('Email notification sent successfully.')
    except Exception as e:
        print('Failed to send email notification:', str(e))

# Function to monitor SSH connections
def monitor_ssh_connections():
    cmd = "journalctl _SYSTEMD_UNIT=ssh.service -f --no-pager"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for line in process.stdout:
        line = line.decode('utf-8').strip()
        #This is a mistake as when devices connect the word by does not exist in the log
        if 'Accepted' in line and 'by' in line and 'from' in line:
            parts = line.split()
            remote_ip = parts[parts.index('from') + 1]
            if not remote_ip.startswith('192.168.'):  # Filter out internal IP connections
                send_email('SSH Connection Detected', f'SSH connection from IP: {remote_ip}')

# Main program
while True:
    # Get the externally facing IP address of the router
    external_ip = get_external_ip()
    if external_ip:
        print('External IP:', external_ip)
        monitor_ssh_connections()
    else:
        print('Failed to retrieve external IP address.')

    # Sleep for a specified interval (e.g., 5 minutes) before checking again
    time.sleep(300)  # Sleep for 5 minutes (adjust as needed)
