#!/usr/bin/env python

# Websocket server for armory pass pw manager chrome extension.
# This requires no parameters to operate, just run it on the armory.
# By default we listen on 0.0.0.0, you might want to refine this.
# See README.md for more details on operation.

# Michael Weissbacher, 2015
# Licensed for personal, non-commercial use only

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool, WebSocket
from ws4py.websocket import EchoWebSocket
from ws4py.messaging import Message
import ConfigParser
import SocketServer
import threading
import random
import string
import time
import json
import sys
import os


cherrypy.config.update({'server.socket_port': 9000, 'server.socket_host': '0.0.0.0' })
WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()

# We only expect one connection from the web browser at a time
ws = None
origin = None
pwmanager = None
conf_filename = "config.ini"

class WSHandler(WebSocket):
    def received_message(self, message):
        global ws
        global origin
        global pwmanager
        global config

        try:
            sec, command = message.data.split(":::")

            if sec != config.get('ws', 'secret'):
                print "Secret does not match, abort"
                return
            ws = self

            print "Received: {0}".format(message.data)
            if command.startswith("ORIGIN="):
                origin = command[len("ORIGIN="):]
                print "Set origin to: {0}".format(origin)
                # Respond with password
                sendstr = "setPassword={0}".format(pwmanager.query_for_origin(origin))
                ws.send(sendstr)
                print "Sent {0}".format(sendstr)
        except Exception as e:
            sys.stderr.write("Error processing WS data: {0}\n".format(e))

class PWManager:

    def __init__(self):
        try:
            self.pwmanager = json.loads(open("password_store.json").read())
        except Exception as e:
            sys.stderr.write("Error reading password file: {0}\n".format(e))
            sys.exit(1)

    def query_for_origin(self, origin):
        for e in self.pwmanager:
            if e['origin'] == origin:
                return e['password']
        return None

class CherryRoot(object):
    @cherrypy.expose
    def index(self):
        return '=> /ws'

    @cherrypy.expose
    def ws(self):
        handler = cherrypy.request.ws_handler


class SockHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global ws
        global config

        if ws == None:
            sys.stderr.write("No Websocket connection\n")
            return

        self.data = self.request.recv(1024).strip()
        try:
            sec, command = self.data.split(":::")
            if command == "BUTTONPRESS":
                if sec == config.get('ws', 'secret'):
                    print "pressed!"
                    ws.send("getOrigin")
                    print "Sent 'getOrigin' to browser"
                else:
                    print "Secret does not match, received: {0}".format(sec)
            self.finish()
        except Exception as e:
            sys.stderr.write("Error parsing: {0}\n".format(e))
            pass
        print self.data


class SSthread(threading.Thread):

    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port

    def run(self):
        server = SocketServer.TCPServer((self.host, self.port), SockHandler)
        server.serve_forever()


# This is polling the cherrypy server status.
# If it is shutting down, we kill the socket server

class WatchdogThread(threading.Thread):

    def __init__(self, ss):
        threading.Thread.__init__(self)
        self.ss = ss

    def run(self):

        while True:
            time.sleep(1)
            if cherrypy.engine.state != cherrypy.engine.states.STARTED:
                self.ss._Thread__stop()
                sys.exit(0)

def get_config(cfile):
    config = ConfigParser.ConfigParser()

    try:
        # "touch"
        if not os.path.isfile(cfile):
            x = open(cfile, 'w')
            x.close()
        config.read(cfile)
        if not config.has_section('ws'):
            config.add_section('ws')
    except Exception as e:
        sys.stderr.write("Exception reading config file: {0}\n".format(e))
        sys.exit(1)
    return config

def get_random_pw():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))

def write_JS_secret_file(sec, fn = "../chrome-extension/secret.js"):
    f = open(fn, "w")
    f.write("// You shouldn't have to modify this file.\n")
    f.write("// If you want to re-generate a key, just delete it\n")
    f.write("// and restart the ws server.\n")
    secret = get_random_pw()
    f.write( "secret = '{0}';\n".format(sec))
    f.close()



def main():
    global pwmanager
    global config


    config = get_config(conf_filename)
    if not config.has_option('ws', 'secret'):
        config.set('ws', 'secret', get_random_pw())
    config.write(open(conf_filename, 'w'))
    write_JS_secret_file(config.get('ws','secret'))

    pwmanager = PWManager()

    # Connections from the fake button
    s = SSthread("localhost", 9001)
    s.start()

    # Watchdog to kill the above thread once we shut down cherrypy
    w = WatchdogThread(s)
    w.start()

    cherrypy.quickstart(CherryRoot(), '/', config={'/ws': {'tools.websocket.on': True,
                                                    'tools.websocket.handler_cls': WSHandler}})
if __name__ == "__main__":
    main()

