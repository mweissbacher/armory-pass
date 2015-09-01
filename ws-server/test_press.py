#!/usr/bin/env python

# This tool sends a "BUTTONPRESS" string to the server on port 9001
# The optional argument is a delay - the chrome extension will only respond
# if the focus is in a browser tab at the moment of pressing.
# To test: give yourself a second or two to switch back into Chrome and focus on a text box.

# Michael Weissbacher, 2015
# Licensed for personal, non-commercial use only

import os
import pdb
import sys
import time
import socket
import ConfigParser


def get_config(cfile):
    config = ConfigParser.ConfigParser()

    try:
        config.read(cfile)
    except Exception as e:
        sys.stderr.write("Exception reading config file: {0}\n".format(e))
        sys.exit(1)
    return config


wait = 0

if len(sys.argv) > 1:
    wait = int(sys.argv[1])

time.sleep(wait)

config=get_config('config.ini')

sock = socket.socket()
sock.connect(('localhost', 9001))
sock.send("{0}:::BUTTONPRESS".format(config.get('ws','secret')))

