import paramiko

host = "192.168.4.51"
user = "username"
password = "password"

script_path = "Downloads/wotm-testing server_thread.py"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=password, timeout=5)
channel = ssh.get_transport().open_session()
channel.get_pty()
channel.exec_command(script_path)
