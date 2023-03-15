import json
import requests
import boto3
import os

# Get the instance ID from the instance metadata service
response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = response.text

# Get the public and private IPs from the instance metadata service
response = requests.get('http://169.254.169.254/latest/meta-data/public-ipv4')
public_ip = response.text
response = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4')
private_ip = response.text

# Get the security group IDs from the instance metadata service
response = requests.get('http://169.254.169.254/latest/meta-data/security-groups')
security_groups = response.text.split('\n')

# Get the operating system name and version from the /etc/os-release file
with open('/etc/os-release') as f:
    os_release = f.read()
    os_name = os_release.split('=')[1].split('\n')[0].strip('"')
    os_version = os_release.split('=')[2].split('\n')[0].strip('"')

# Get the list of users with permission to bash or sh shells
users = []
with os.popen('getent passwd') as f:
    for line in f:
        user = line.split(':')[0]
        shell = line.split(':')[-1].strip()
        if shell.endswith('/bash') or shell.endswith('/sh'):
            users.append(user)

# Save the collected data to a file
data = {
    'instance_id': instance_id,
    'public_ip': public_ip,
    'private_ip': private_ip,
    'security_groups': security_groups,
    'os_name': os_name,
    'os_version': os_version,
    'users': users
}
with open('/tmp/instance_data.json', 'w') as f:
    f.write(json.dumps(data))

# Upload the file to an S3 bucket
s3 = boto3.client('s3')
bucket_name = 'applicant-task'
key = 'instance_data.json'
s3.upload_file('/tmp/instance_data.json', bucket_name, key)
