"""
Script to read data from UART with FTDI

Copyright (c) 2022 Valerio Spinogatti
Licensed under GNU license

ftdi_read_uart.py
"""

import pyftdi.serialext as pser
import pyftdi.ftdi as ftdi
import serial.serialutil
from signal import signal, SIGINT
from argparse import ArgumentParser


def exit_handler(signal_received, frame):
    print('\n\nSIGINT or CTRL-C detected. Exiting gracefully.')
    exit(0)


def find_devices():
    possible_ftdi_devices = ftdi.Ftdi.list_devices()
    print(f"\nFound {len(possible_ftdi_devices)} FTDI devices.")
    for n, dev in enumerate(possible_ftdi_devices):
        print(f"\nDevice {n}:")
        for key, elem in zip(dev[0]._fields, dev[0]):
            print(key, "=", elem)
    print("\n")

    if len(possible_ftdi_devices) == 0:
        print("Warning. No devices found.\n")
        return None

    elif len(possible_ftdi_devices) == 1:
        vid = possible_ftdi_devices[0][0][0]
        pid = possible_ftdi_devices[0][0][1]
        bus = possible_ftdi_devices[0][0][2]
        addr = possible_ftdi_devices[0][0][3]
        # sernum = possible_ftdi_devices[0][0][4]
        return f"ftdi:///1"

    elif len(possible_ftdi_devices) > 1:
        print("Warning: more than one FTDI device found. \nReturning URL of the first one that was enumerated.")
        vid = possible_ftdi_devices[0][0][0]
        pid = possible_ftdi_devices[0][0][1]
        bus = possible_ftdi_devices[0][0][2]
        addr = possible_ftdi_devices[0][0][3]
        # sernum = possible_ftdi_devices[0][0][4]
        return f"ftdi://{str(hex(vid))}:{str(hex(pid))}:{bus}:{addr}/1"

def main():
    #Parse arguments
    p = ArgumentParser(description = "Program for reading utf-8 encoded UART bytes with FTDI.")

    p.add_argument("baudrate",
                    type = int,
                    help = "Baudrate of UART interface.")

    p.add_argument("-u",
                    "--url",
                    type = str,
                    help = "URL of the FTDI device.")
    
    args = p.parse_args()

    # Read-only variables
    BAUDRATE = args.baudrate
    STANDARD_BAUDRATES = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]

    if BAUDRATE not in STANDARD_BAUDRATES:
        raise Warning("Baudrate value is not a standard value.")

    # Registering ctrl+c callback
    signal(SIGINT, exit_handler)

    # Print useful information
    print("\nProgram for reading utf-8 encoded UART bytes with FTDI. Hit CTRL+C to terminate.")

    # Find device(s)
    if args.url is None:
        device_url = find_devices()
        if not device_url:
            raise OSError("No FTDI device found. Exiting.")
    else:
        device_url = args.url

    print("Connecting to device with URL ", device_url)
    print("Received bytes:")

    try:
        ftdi_dev = pser.serial_for_url(device_url, baudrate = BAUDRATE)
    except serial.serialutil.SerialException as e:
        raise OSError(e)

    # Main while loop
    while True:
        try:
            received_bytes = ftdi_dev.read(32)
        except UnicodeDecodeError as e:
            print("\nThere was an error while decoding received bytes. Maybe some bytes have been corrupted.\n")
            print(e)
        print(received_bytes.hex())


if __name__ == "__main__":
    main()  