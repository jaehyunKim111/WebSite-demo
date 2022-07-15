var handler = document.querySelector('.handler');
var wrapper = handler.closest('#content');
var boxA = wrapper.querySelectorAll('#element')[1]; // element #element <div id = "element">
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
  


  boxA.style.width = pointerRelativeXpos - 8 + 'px';
  boxA.style.flexGrow = 0;
});

document.addEventListener('mouseup', function(e) {
  // Turn off dragging flag when user mouse is up
  isHandlerDragging = false;
});