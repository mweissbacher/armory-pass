// Armory Pass Background Script

// Michael Weissbacher 2015
// Licensed for personal, non-commercial use only

var wsUri = "ws://127.0.0.1:9000/ws"; // for testing


// This is the default armory IP, if yours is different, edit *here*.
// var wsUri = "ws://10.0.0.1:9000/ws";
var websocket = null;

if ( typeof(secret) === "undefined" ) {
    alert("Armory Pass: could not read file 'secret.js', please run ws.py first and reload");
}

// This sends a message to the content script
function getOriginFromContentScript(sendResponse) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {

      if(tabs.length === 0 ) {
        console.log("No active tabs?");
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, {action: "getOrigin"}, function(response) {
        console.log(response);
        if (typeof(response) == "undefined") {
            console.log("Something went wrong");
            return;
        }
        var activeorigin = response.activeorigin;
        console.log(activeorigin);
        sendResponse(secret + ":::ORIGIN=" + activeorigin);
      });
    });
}

// This sends the password to be set in the textfield
function setPasswordInTextField(sendResponse, pw) {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {

      if(tabs.length === 0 ) {
        console.log("No active tabs?");
        return;
      }

      chrome.tabs.sendMessage(tabs[0].id, {action: "setPassword", password: pw}, function(response) {
        console.log(response);
        if (typeof(response) == "undefined") {
            console.log("Something went wrong");
            return;
        }
        console.log(response.activeorigin);
      });
    });
}

///// Websockets

function wsOnOpen(evt) {
    console.log("CONNECTED to: " + wsUri);
    // Any message is fine, just don't forget the password
    wsDoSend(secret + ':::x')
}

function wsOnClose(evt) {
    console.log("DISCONNECTED");
}

function wsOnMessage(evt) {
    console.log('RESPONSE: ' + evt.data);
    if ( evt.data === "getOrigin" ) {
        getOriginFromContentScript(wsDoSend);
    } else if ( evt.data.startsWith("setPassword")) {
        var pw = evt.data.substr(12, evt.data.length);
        setPasswordInTextField(wsDoSend, pw);
    }
}

function wsOnError(evt) {
    console.log('ERROR: ' + evt.data);
}

function wsDoSend(message) {
    console.log("SENT: " + message);
    websocket.send(message);
}


function wsSetup () {

    if ( websocket == null || websocket.readyState === websocket.CLOSED || websocket.readyState === websocket.CLOSING ) {
        websocket = new WebSocket(wsUri);
        websocket.onopen = function(evt) {
            wsOnOpen(evt)
        };  
        websocket.onclose = function(evt) {
            wsOnClose(evt)
        };  
        websocket.onmessage = function(evt) {
            wsOnMessage(evt)
        };  
        websocket.onerror = function(evt) {
            wsOnError(evt)
        };  
    }
}

function init(e) {
    //document.getElementById('armorybutton').onclick=getOriginFromContentScript;
    wsSetup();
    // We poll the connection once every two seconds
    setInterval(wsSetup, 2000);
}

window.addEventListener("load", init, false);

