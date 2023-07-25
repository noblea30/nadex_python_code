'use strict';

var cdnBaseUrl = "https://cdn.getsupernova.com";

function log(msg) {
  console.log("Supernova Extension - background - "+msg);
}

var lastPingedSuperStarterMs=Date.now()-MAXPINGRATE*2;
var MAXPINGRATE = 5000;

var lastRanSuperStarterMs=Date.now()-MAXRUNRATE*2;
var MAXRUNRATE = 3500;

var isSetup=false;
var messageFrame=null;

//chrome.runtime.setUninstallURL(cdnBaseUrl+"/uninstall_extension.html", function() {log("Extension uninstalled")});

function checkExtensionStatus(cb) {
  chrome.storage.local.get(["superstarter"], function(result) {    
    if(result!=null && typeof(result)=='object') {
      var superStarterInfo = result["superstarter"];
      var installed = (superStarterInfo && typeof(superStarterInfo)==='object' && superStarterInfo.installed);      
      messageFrame.contentWindow.postMessage({command:"superstarterstatus",data:{installed:installed}},cdnBaseUrl);
      if(cb) cb({
        extension:true,
        superstarter:superStarterInfo.installed
      });        
    }
  });
}

function launchSuperStarter(play) {
  if(lastRanSuperStarterMs > Date.now() - MAXRUNRATE) {    
    return;
  }
  lastRanSuperStarterMs = Date.now();

  chrome.runtime.sendNativeMessage('com.tacticstechnology.superstarter',    
    { text: play },
    function (response) {
      if(response == null) {
        log("Superstarter failed to launch - running check on status");
        checkSuperStarterStatus();
      } else {
        log("Received " + JSON.stringify(response));
      }
    });
}


function checkSuperStarterStatus(cb) {
  if(lastPingedSuperStarterMs > Date.now() - MAXPINGRATE) {
    cb(null);
    return;
  }
  lastPingedSuperStarterMs = Date.now();

  chrome.runtime.sendNativeMessage('com.tacticstechnology.superstarter',    
    { text: "ping" },
      function(r) {
        var storageObj = {};
        if(r) {
          messageFrame.contentWindow.postMessage({command:"superstarterstatus",data:{installed:true}},cdnBaseUrl);
          storageObj["superstarter"] = {installed:true};
        } else {
          messageFrame.contentWindow.postMessage({command:"superstarterstatus",data:{installed:false}},cdnBaseUrl);
          storageObj["superstarter"] = {installed:false};
        }
        chrome.storage.local.set(storageObj, function() {});
        if(cb) cb(r);
      }
  );
}



function setupMessageFrame() {
  if(isSetup) return true;
  var el = document.body;
  if(el == null) return false;

  messageFrame = document.createElement("iframe");
  messageFrame.id="supernovamessageframe";
  messageFrame.onload=checkSuperStarterStatus.bind(null,null);
  messageFrame.src=cdnBaseUrl+"/tags/message_frame.html";
  messageFrame.scrolling="no";
  messageFrame.width="0";
  messageFrame.height="0";
  
  el.appendChild(messageFrame);			
  isSetup=true;

  return true;
}

setupMessageFrame();




function isValidTab(tab) {
  if (tab == null) return false;
  var url = new URL(tab.url);
  if (url.protocol == "https:" || url.protocol == "http:") {
    return true;
  }
  return false;
}


chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  switch(message.command) {
    case "getextensionstatus":
      checkExtensionStatus(function(r) {
        sendResponse(r);      
      });
      return true; //async sendResponse.
    case "superstarter":
      if(message.data) {
        sendResponse("superstarter - launched");
        launchSuperStarter(message.data);
        //runZoneTag();
      }  
    break;    
    }
});


chrome.runtime.onInstalled.addListener(function () { 
  chrome.tabs.query({currentWindow: true}, function (tabs) {
    for (var i = 0; i < tabs.length; i++) {
      if (isValidTab(tabs[i])) {
        chrome.tabs.reload(tabs[i].id);
      }
    }
  });
});
