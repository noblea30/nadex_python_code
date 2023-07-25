var superstarterMessageData = null;
var splashObject = null;
var extensionStatus = {
  extension:true
}
var installStatus = {};
var launchStatus = {};

chrome.runtime.sendMessage({"command":"getextensionstatus"}, function(result) {        
  if(result!=null && typeof(result)=='object') {
    extensionStatus = result;
  }
});

//FIXME: Add  optional deep scanning  capability of 1-2 levels of iframes for getBestObjectEl/getSplashObject)
//For speed reasons, perhaps only enable on sites/pages where user has enabled flash manually before?
function getBestObjectEl(searchDepth) {
  var embeds = document.getElementsByTagName("object");
  var maxembed = null;
  var maxembedwidth = 300;
  var maxembedheight = 200;
  for (var i = 0; i < embeds.length; i++) {
      var embed = embeds[i];
      if (parseInt(embed.width) > maxembedwidth && parseInt(embed.height) > maxembedheight ||
         parseInt(embed.clientWidth) > maxembedwidth && parseInt(embed.clientHeight) > maxembedheight) {
          maxembedwidth = parseInt(embed.width);
          maxembedheight = parseInt(embed.height);
          maxembed = embed;
      }
  }
  return maxembed;
  }

function getSplashObject() {
  var bestObjectEl = getBestObjectEl();
  if (bestObjectEl) {
      var bestEmbed = bestObjectEl.querySelector("embed");
      var flashvarsEl = bestObjectEl.querySelector("param[name=flashvars],param[name=Flashvars],param[name=flashVars],param[name=FlashVars]");
      
      var movieUrl = bestEmbed!=null?bestEmbed.src:null;                
      if(movieUrl == null) {
          movieUrl = bestObjectEl.getAttribute("data");
          if(movieUrl == null) {
              var movieEl = bestObjectEl.querySelector("param[name=movie],param[name=Movie]");
              if(movieEl != null) {
                  movieUrl = movieEl.getAttribute("value");
              }
          }
      }
      if(movieUrl == null) return null;
      
      var flashvars="";
      if(flashvarsEl){
          flashvars = flashvarsEl.value;
      }
      if(flashvars===""){
          flashvars = bestObjectEl.getAttribute("flashvars");
      }
      return {
          width: parseInt(bestObjectEl.width),
          height: parseInt(bestObjectEl.height),
          url: movieUrl,
          objectEl: bestObjectEl,
          flashvars:flashvars
      }
  }	
  return null;
}    

function addEventHandler(eventName, cb) {
  if(window.addEventListener) {
      window.addEventListener(eventName, cb, false);
  } else {
      window.attachEvent(eventName, cb);
  };
}
function sendMessageToPage(message)
{    
    var eventInit = {
      data: {
        key:"supernova-extension-message",
        message: JSON.stringify(message)
      }
    };
    var event = new MessageEvent('supernova-message', eventInit);
    window.dispatchEvent( event );
}
function sendStatusToPage() {
  sendMessageToPage({command:"status",data:{
    launchStatus:launchStatus,
    extensionStatus:extensionStatus
  }});
}
function superNovaMessageEventHandler(e)
{    
    if(!e.data || !e.data.message) return;
    if(e.data.key != "supernova-jslauncher-message") return;
    var message = null;
    try { 
        message = JSON.parse(e.data.message);
    } catch(e) {
        return;
    }
    if(!message) return;
        
    switch(message.command) {
        case "requeststatus":          
          sendStatusToPage();            
          break;
        case "status":
          if(message.data.launchStatus) {
            launchStatus = extend(launchStatus, message.data.launchStatus);
            launchStatusReceived = true;
          }
          break;
        case "supernovaplayerstatus":
            if(message.data && message.data.installed) {
              extend(installStatus,{detected:true});                        
            } else {
              extend(installStatus,{detected:false});
            }
          break;
    }
} 
addEventHandler("supernova-message", superNovaMessageEventHandler);

/*!    SWFObject v2.3.20130521 <http://github.com/swfobject/swfobject>
		is released under the MIT License <http://www.opensource.org/licenses/mit-license.php>
		Copyright (c) 2007-2015 The SWFObject team
*/

var ua = function () {
  function toInt(str) {
    return parseInt(str, 10);
  }


  let doc = document, nav = navigator, win = window,
    UNDEF = "undefined",
    OBJECT = "object",
    SHOCKWAVE_FLASH = "Shockwave Flash",
    SHOCKWAVE_FLASH_AX = "ShockwaveFlash.ShockwaveFlash",
    FLASH_MIME_TYPE = "application/x-shockwave-flash",
    EXPRESS_INSTALL_ID = "SWFObjectExprInst",
    ON_READY_STATE_CHANGE = "onreadystatechange",
    plugin = false;

  var w3cdom = typeof doc.getElementById !== UNDEF && typeof doc.getElementsByTagName !== UNDEF && typeof doc.createElement !== UNDEF,
    u = nav.userAgent.toLowerCase(),
    p = nav.platform.toLowerCase(),
    windows = p ? /win/.test(p) : /win/.test(u),
    mac = p ? /mac/.test(p) : /mac/.test(u),
    webkit = /webkit/.test(u) ? parseFloat(u.replace(/^.*webkit\/(\d+(\.\d+)?).*$/, "$1")) : false, // returns either the webkit version or false if not webkit
    ie = nav.appName === "Microsoft Internet Explorer",
    playerVersion = [0, 0, 0],
    d = null;
  if (typeof nav.plugins !== UNDEF && typeof (nav.plugins)[SHOCKWAVE_FLASH] === OBJECT) {
    d = (nav.plugins)[SHOCKWAVE_FLASH].description;
    // nav.mimeTypes["application/x-shockwave-flash"].enabledPlugin indicates whether plug-ins are enabled or disabled in Safari 3+
    if (d && (typeof nav.mimeTypes !== UNDEF && (nav.mimeTypes)[FLASH_MIME_TYPE] && (nav.mimeTypes)[FLASH_MIME_TYPE].enabledPlugin)) {
      plugin = true;
      ie = false; // cascaded feature detection for Internet Explorer
      d = d.replace(/^.*\s+(\S+\s+\S+$)/, "$1");
      playerVersion[0] = toInt(d.replace(/^(.*)\..*$/, "$1"));
      playerVersion[1] = toInt(d.replace(/^.*\.(.*)\s.*$/, "$1"));
      playerVersion[2] = /[a-zA-Z]/.test(d) ? toInt(d.replace(/^.*[a-zA-Z]+(.*)$/, "$1")) : 0;
    }
  }
  else if (typeof (win).ActiveXObject !== UNDEF) {
    try {
      //@ts-ignore
      var a = new ActiveXObject(SHOCKWAVE_FLASH_AX);
      if (a) { // a will return null when ActiveX is disabled
        d = a.GetVariable("$version");
        if (d) {
          ie = true; // cascaded feature detection for Internet Explorer
          d = d.split(" ")[1].split(",");
          playerVersion = [toInt(d[0]), toInt(d[1]), toInt(d[2])];
        }
      }
    }
    catch (e) { }
  }
  return { w3: w3cdom, pv: playerVersion, wk: webkit, ie: ie, win: windows, mac: mac };
}();

function getFlashPlayerVersion() {
  return { major: this.ua.pv[0], minor: this.ua.pv[1], release: this.ua.pv[2] };
}
/* end SWFObject */
function hasFlashPlayerVersion(flashver) {
  let fv = flashver.split(".");
  let a = this.getFlashPlayerVersion();
  let keys = Object.keys(a);
  for(let i=0;i<3; i++){
    fv[i] = parseInt(fv[i] || 0);
  }
  return ((fv[0] <= a.major) || (fv[0] === a.major && fv[1] <= a.minor)) || (fv[0]===a.major && fv[1]===a.minor && fv[2].release <= a.release);
}

function extend(dst, src) {
  var keys = Object.keys(src);
  for(var k=0; k<keys.length; k++){
      var key= keys[k];
      dst[key]=src[key];
  }
  return dst;
}

var hash = window.location.hash
var log = function(m) {}

if(hash == "#snDev" || hash == "#snLog") {
  log = console.log.bind(window.console)
} else {  
}

function addEventHandler(eventName, cb) {
  if(window.addEventListener) {
    window.addEventListener(eventName, cb, false);
  } else {
    window.attachEvent(eventName, cb);
  };
}


function getLaunchStatus() {
  return launchStatus;
}
function setLaunchStatus(data) {

  return extend(installStatus, data);
}
function getInstallStatus() {
  return installStatus;
}
function setInstallStatus(data) {
  return extend(installStatus, data);
}


//Listener to accept messages from the page itself to tell us if they launched supernova via scheme
function receiveMessage(e)
{		    
    //if (e.source != window) return;    //FIXME: Anyone can post commands
    var message = e.data;

		if(typeof(message)=== "object") {      
      switch(message.command) {
        case "superstarter":            
            if(message.data) {
              superstarterMessageData = message.data;
              setLaunchStatus({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});
              chrome.runtime.sendMessage({"command":"superstarter","data":message.data}, function(response) {
                log("Enabled superstarter!");
                window.postMessage(JSON.stringify({event:"superstarter",status:"started",data:"manual"}), "*");
                
                setLaunchStatus({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});
        
                //alert("Enabled superstarter!");
              }
              );            
            }
      }
    }
}
window.addEventHandler("message",receiveMessage);

function processSuperStarterRequest(splashObject, sendResponse) {
  if(splashObject!=null) {
    var command = "play?swfurl="+encodeURIComponent(splashObject.url)+"&flashvars="+encodeURIComponent(splashObject.flashvars);
    chrome.runtime.sendMessage({"command":"superstarter","data":command}, function(response) {
      log("Enabled superstarter!");
      window.postMessage(JSON.stringify({event:"superstarter",status:"started",data:"manual"}), "*");
      
      sendResponse({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});
      setLaunchStatus({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});

      //alert("Enabled superstarter!");
    });
    return true;
  } else if(superstarterMessageData!=null) {
    setLaunchStatus({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});
    chrome.runtime.sendMessage({"command":"superstarter","data":superstarterMessageData}, function(response) {
      log("Enabled superstarter!");
      window.postMessage(JSON.stringify({event:"superstarter",status:"started",data:"manual"}), "*");
      
      setLaunchStatus({launchStatus:"started",launchType:"manual",launchMethod:"superstarter"});

      //alert("Enabled superstarter!");
    }
    );            
  } else {
    sendResponse({});
  }    
}


//Listener to accept messages from the background/ui
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  switch(message.data) {
  case "runRuffle":
      runRuffle();
      break;  
  case "getLaunchStatus":
    sendResponse(getLaunchStatus())          
    break;
  case "superstarterrequest":
    var splashObject = getSplashObject();    
    processSuperStarterRequest(splashObject, sendResponse);
    

  case "closeNotification":
    //log(document.getElementById("enablerDiv2"));
    var enablerDiv2 = document.getElementById("enablerDiv2")
    if(enablerDiv2) {
      enablerDiv2.style.display = 'none';  
    }
    break;
  case "dismissNotification":
    var enablerDiv2 = document.getElementById("enablerDiv2")
    if(enablerDiv2) {
      enablerDiv2.style.display = 'none';  
    }
    var storageObj = {};
    storageObj[window.location.host] = {"dismissed":new Date().getTime()};
    chrome.storage.local.set(storageObj, function() {
        log('Dismissed is set to true');
    })              
    
    //chrome.runtime.sendMessage({"command":"dismissFlashPrompt"});

    break;
  }
});
 
