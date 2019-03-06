var bodyHtml = "" +
"<h1><center>DG Kernel Automatic Performance Optimization(Prototype)</center></h1>" +
"<div><br></div>" +
"<div class='box'>Current Status</div>" +
"<div><br></div>" +
"<div class='wrapper'>" +
"  <div class='box'>Current Code</div>" +
"  <div class='handler'></div>" +
"  <div class='box'>Current Mesurement</div>" +
"</div>" +
"<div><br></div>" +
"<div class='box'>Selecting next optimization</div>"

document.body.innerHTML = bodyHtml;

var handler = document.querySelector('.handler');
var wrapper = handler.closest('.wrapper');
var boxA = wrapper.querySelector('.box');
var isHandlerDragging = false;

document.addEventListener('mousedown', function(e) {
  // If mousedown event is fired from .handler, toggle flag to true
  if (e.target === handler) {
    isHandlerDragging = true;
  }
});

document.addEventListener('mousemove', function(e) {
  // Don't do anything if dragging flag is false
  if (!isHandlerDragging) {
    return false;
  }

  // Get offset
  var containerOffsetLeft = wrapper.offsetLeft;

  // Get x-coordinate of pointer relative to container
  var pointerRelativeXpos = e.clientX - containerOffsetLeft;
  
  // Arbitrary minimum width set on box A, otherwise its inner content will collapse to width of 0
  var boxAminWidth = 60;

  // Resize box A
  // * 8px is the left/right spacing between .handler and its inner pseudo-element
  // * Set flex-grow to 0 to prevent it from growing
  boxA.style.width = (Math.max(boxAminWidth, pointerRelativeXpos - 8)) + 'px';
  boxA.style.flexGrow = 0;
});

document.addEventListener('mouseup', function(e) {
  // Turn off dragging flag when user mouse is up
  isHandlerDragging = false;
});

pyloco.onOpen(function openHandler (evt) {
    window.console.log(evt);
});

pyloco.onClose(function closeHandler (evt) {
    window.console.log(evt);
});

pyloco.onMessage("dgkernel", "refcase", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "refsrc", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "refout", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "refmeasure", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "case", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "src", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "out", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onMessage("dgkernel", "measure", function messageHandler (msgId, ts, msg) {
    window.console.log(msg);
});

pyloco.onError(function errorHandler (evt) {
    window.console.log(evt);
});

