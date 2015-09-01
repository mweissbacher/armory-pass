# Overview:
The purpose of this tool is to provide functionality similar to browser-based password managers.
However, the passwords are stored on the USB Armory and only revealed one at a time via button press.
The goal is to prevent copying of the whole password file (e.g., LastPass container).
The Armory will surrender the password for the currently active site only, and only when you press the button.
We wrote a Chrome extension that informs the armory in what origin the current focus is.

This approach has some limitations, e.g., for now only one password per origin is possible, and we do not support usernames.
These features may be possible with a more advanced GUI in the future, but for now will remain as a TODO note.

## A note on "the button":
The armory currently has no button, but you can add one yourself via general I/O!
However, to allow for playing around we included the script test\_press.py that sends a command that will set things in motion.
Just make sure to trigger that script via button press.
See here for some button infos: https://github.com/crmulliner/hidemulation

## Main components:
- Chrome Extension (sorry FireFox users)
- WebSocket + regular Socket server (runs on armory)

### The Chrome extension:
The background script connects to the websocket and listens for commands.
When commands are received ('getOrigin') the request is relayed to the content script in the active tab, which answers accordingly.

### Server:
The server has a long lasting connection to the chrome extension (WebSockets, port 9000), and can be sent "BUTTONPRESS" on port 9001.
This buttonpress queries the Chrome extension for the current origin, and then sends the password for that field.

## Setup:

First, figure out the IP address of your USB armory.
ws.py is configured to listen on 0.0.0.0, you might want to restrict this.
Next, change background.js (var wsUri) and manifest.json (permissions) to make sure the extension connects to the right place.
Then, run the server to generate the "secret.js" file which has to be available to the Chrome extension (same folder as background.js)
This is necessary for authentication.
When launched, the chrome extension connects to the websocket server.
When disconnected, it will start polling the WebSocket server periodically until reconnected.
To install the chrome extension enable "developer mode" ( chrome://extensions/ ) and use "Load unpacked extension".
I purposefully did not package this for the app store for now.

## Usage:
- Add passwords to password\_store.json
- Navigate to the site you want to log into
- Click the password field
- Press the button on your USB Armory

# Misc

## A Note on Content Security Policy:
We use "unsafe-eval" for one purpose only: polling the status of the WebSocket connection. Code is not constructed from strings.

## TODO:
- Usernames
- Multiple Passwords

