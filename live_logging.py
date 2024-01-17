import paramiko
import time


def tail_rpi_log(remote_host, username, password, log_file_path):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()

        # Automatically add the Raspberry Pi's host key
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the Raspberry Pi
        ssh.connect(remote_host, username=username, password=password)

        # Continuously tail the log file
        while True:
            # Open an SFTP session to transfer the log file
            sftp = ssh.open_sftp()

            # Download the log file from the Raspberry Pi to the local machine
            local_log_file_path = "local_log.txt"
            sftp.get(log_file_path, local_log_file_path)

            # Close the SFTP session
            sftp.close()

            with open(local_log_file_path, "r") as log_file:
                log_file.seek(0, 2)  # Move the file cursor to the end
                new_line = log_file.readline()
                if new_line:
                    print(new_line.strip())

            # Sleep for a short duration before checking for new logs
            time.sleep(1)

    except Exception as e:
        print(f"Error: {str(e)}")

    finally:
        # Disconnect from the Raspberry Pi
        ssh.close()


if __name__ == "__main__":
    # Replace these values with your Raspberry Pi's information
    # Replace with the IP address or hostname of your Raspberry Pi
    remote_host = "raspberrypi.local"
    username = "your_username"
    password = "your_password"
    # Replace with the actual path to your log file
    log_file_path = "/path/to/your/log/file.log"

    tail_rpi_log(remote_host, username, password, log_file_path)
