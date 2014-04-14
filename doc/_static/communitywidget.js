var showWidget = true;

if (showWidget) {

   var widget = document.getElementById("communityWidget");
   var parentUrl = window.location.host;

   widget.classList.add("min");
   widget.classList.remove("nonDisplay");

   function onIFrameMessage(evt) {

      var targetSize = evt.data;

      if (targetSize === "min") {

         widget.classList.remove("max");
         widget.classList.add("min");

      } else if (targetSize === "max") {

         widget.classList.remove("min");
         widget.classList.add("max");
      }
   }

   window.addEventListener("message", onIFrameMessage);
}


// detect user interacting with the page / tab
// message this to the community widget iframe

document.addEventListener("click", onInterActionDetected);
document.addEventListener("keydown", onInterActionDetected);
document.addEventListener("mousemove", onInterActionDetected);
document.addEventListener("mousedown", onInterActionDetected);
document.addEventListener("mouseup", onInterActionDetected);
document.addEventListener("wheel", onInterActionDetected);

// for touch devices
document.addEventListener("touchstart", onInterActionDetected);
document.addEventListener("touchend", onInterActionDetected);
document.addEventListener("touchmove", onInterActionDetected);

window.addEventListener("focus", onInterActionDetected);
window.addEventListener("blur", onInterActionDetected);

var messageTarget = document.getElementById("communityWidget").contentWindow;

function onInterActionDetected(evt) {
   var actionType = evt.type;
   var source = window.location.href;
   messageTarget.postMessage([actionType, source], "*");
}


// change widget position on scrolling
var widgetOffsetY = widget.getClientRects()[0].top;

window.addEventListener("scroll", function() {
   var widget = document.getElementById("communityWidget");
   var windowOffsetY = window.pageYOffset;
   var curWoY = widget.getClientRects()[0].top;
   var newOffSet;

   curWoY = widgetOffsetY - windowOffsetY;
   curWoY < 0 ? curWoY = 0 : curWoY = curWoY;

   widget.style.top = curWoY + "px";
})
var showWidget = true;

if (showWidget) {

   var widget = document.getElementById("communityWidget");
   var parentUrl = window.location.host;

   widget.classList.add("min");
   widget.classList.remove("nonDisplay");

   function onIFrameMessage(evt) {

      var targetSize = evt.data;

      if (targetSize === "min") {

         widget.classList.remove("max");
         widget.classList.add("min");

      } else if (targetSize === "max") {

         widget.classList.remove("min");
         widget.classList.add("max");
      }
   }

   window.addEventListener("message", onIFrameMessage);
}


// detect user interacting with the page / tab
// message this to the community widget iframe

document.addEventListener("click", onInterActionDetected);
document.addEventListener("keydown", onInterActionDetected);
document.addEventListener("mousemove", onInterActionDetected);
document.addEventListener("mousedown", onInterActionDetected);
document.addEventListener("mouseup", onInterActionDetected);
document.addEventListener("wheel", onInterActionDetected);

// for touch devices
document.addEventListener("touchstart", onInterActionDetected);
document.addEventListener("touchend", onInterActionDetected);
document.addEventListener("touchmove", onInterActionDetected);

window.addEventListener("focus", onInterActionDetected);
window.addEventListener("blur", onInterActionDetected);

var messageTarget = document.getElementById("communityWidget").contentWindow;

function onInterActionDetected(evt) {
   var actionType = evt.type;
   var source = window.location.href;
   messageTarget.postMessage([actionType, source], "*");
}


// change widget position on scrolling
var widgetOffsetY = widget.getClientRects()[0].top;

window.addEventListener("scroll", function() {
   var widget = document.getElementById("communityWidget");
   var windowOffsetY = window.pageYOffset;
   var curWoY = widget.getClientRects()[0].top;
   var newOffSet;

   curWoY = widgetOffsetY - windowOffsetY;
   curWoY < 0 ? curWoY = 0 : curWoY = curWoY;

   widget.style.top = curWoY + "px";
})
