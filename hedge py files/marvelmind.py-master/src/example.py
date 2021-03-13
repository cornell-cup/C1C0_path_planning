from marvelmind import MarvelmindHedge
from time import sleep
import sys
import os
import subprocess

def main():
    # TODO: automate reading usb serial name
    # res = os.system("ls /dev/tty.usb*")
    # get usb port with ls /dev/tty.usb*
    hedge = MarvelmindHedge(tty = "/dev/tty.usbmodem00000000050C1", adr=97, debug=False) # create MarvelmindHedge thread
    hedge.start() # start thread
    while True:
        try:
            sleep(1)
            # print (hedge.position()) # get last position and print
            hedge.print_position()
            if (hedge.distancesUpdated):
                hedge.print_distances()
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port
            sys.exit()
main()
