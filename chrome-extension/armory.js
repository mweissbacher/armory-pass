// Armory Pass Content script.

// Michael Weissbacher 2015
// Licensed for personal, non-commercial use only
DEBUG = true;

// returns the active element origin
function getActiveElementOrigin (e) {
    var active = document.activeElement.ownerDocument.origin;
    if (DEBUG) {
        console.log("Active Element Origin: " + active);
    }
    return active;
};

function setPasswordInField (pw) {
    var active = document.activeElement;
    active.value = pw;
}

if (DEBUG) {
    console.log("Armory Pass content script loaded.");
}

// This listens to messages from the extension,
// and responds with the active origin
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (sender.tab) {
        // this should not happen - extension only.
        return;
    }

    if(DEBUG) {
        console.log("Received Message! " + request.action);
    }

    console.log(sender);
    if(request.action === "getOrigin") {
        sendResponse({activeorigin: getActiveElementOrigin()});
    } else if ( request.action === "setPassword" ) {
        setPasswordInField(request.password);
    } else {
        console.log("Unrecognized command: " + JSON.stringify(request));
    }
  });

