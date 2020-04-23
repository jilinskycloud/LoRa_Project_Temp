function blink_text() {
    $('.blink').fadeOut(500);
    $('.blink').fadeIn(500);
}
setInterval(blink_text, 1000);


















/*###################
Flash Message 
####################*/

window.setTimeout(function() {
  $("#alert_message").fadeTo(500, 0).slideUp(500, function(){
    $(this).remove();
  });
}, 1500);





 
