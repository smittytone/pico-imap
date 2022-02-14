#!/usr/bin/env python3

'''
IMPORTS
'''
import imaplib
import email
import serial
from time import sleep


'''
CONSTANTS
'''
IMAP_HOST = ""
IMAP_PORT = 993
RECHECK_PERIOD_S = 5 * 60


'''
Add a `secrets.py` to your filesystem that has a dictionary called `secrets`
with the following keys:
* "mail", "password" -- your email credentials
* "dev"              -- path/to/your/device
* "host"             -- your IMAP server
DO NOT share that file or commit it into Git or other source control.
'''
try:
    from secrets import secrets
    if not "mail" in secrets: raise
    if not "password" in secrets: raise
    if not "dev" in secrets: raise
    if not "host" in secrets: raise
    IMAP_HOST = secrets["host"]
except ImportError:
    print("[ERROR] Email credentials are stored in `secrets.py`, please add them there")
    raise


'''
Functions
'''

'''
Write out a text string to the serial port
'''
def serial_write(serial_port, msg):
    try:
        if serial_port:
            serial_port.write(msg.encode('utf-8'))
        else:
            print("[ERROR] Missing port")
    except:
        print("[ERROR] Port write fail")


'''
RUNTIME START
'''
if __name__ == '__main__':
    port = None
    try:
        port = serial.Serial(port=secrets["dev"], baudrate=115200)
    except:
        print("[ERROR] Invalid device:", secrets["dev"])
        exit(1)

    # Start the main program loop
    while True:
        # Connect to the IMAP inbox
        imap_server = imaplib.IMAP4_SSL(host=IMAP_HOST, port=IMAP_PORT)
        imap_server.login(secrets["mail"], secrets["password"])
        imap_server.select()

        # Find all the unseen emails in the inbox
        _, message_numbers_raw = imap_server.search(None, 'UNSEEN')
        message_numbers = message_numbers_raw[0].split()
        count = len(message_numbers)
        if count > 0:
            print(f"[DEBUG] {count} new emails in inbox")
            out = ""
            if count == 1:
                out = f"{count} NEW MESSAGE:"
            else:
                out = f"{count} NEW MESSAGES:"

            # Get the new messages' subject lines
            for message_number in message_numbers:
                _, msg = imap_server.fetch(message_number, '(RFC822)')
                message = email.message_from_bytes(msg[0][1])
                out += f' {message["subject"]},'

            out = out[:-1] + "\r"
            # Write the assembled string out
            print(out)
            serial_write(port, out)
        else:
            _, message_numbers_raw = imap_server.search(None, 'ALL')
            message_numbers = message_numbers_raw[0].split()
            out = f"0/{len(message_numbers)} NEW MESSAGES IN INBOX\r"
            serial_write(port, out)

        # Close the connection to the IMAP server
        imap_server.close()
        imap_server.logout()

        # Wait a while
        sleep(RECHECK_PERIOD_S)
