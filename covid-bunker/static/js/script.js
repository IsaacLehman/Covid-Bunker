//scripts go here

// add a listener so that when the document loads . . .
// new listeners  can be attched to elements safely
window.addEventListener("DOMContentLoaded", function() {
  let add_to_cart_buttons = document.querySelectorAll('.add_to_cart');
  for (var i = 0; i < add_to_cart_buttons.length; i++) {
    add_to_cart_buttons[i].addEventListener('click', function(e) {
      // get the VALUE
      let pid = e.target.value;
      console.log(e.target);
      ajax_add_to_cart(pid);
    });
  }



});

// executes a request to a given path and returns the response
function ajax_add_to_cart(pID) {
  path = '/ajax_request/'; // where to send the request
  request = 'pid=' + pID;
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      console.log(http.response);
    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened');
    }
  }

  http.open('POST', path, true); // asynchronus ajax_request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.send(request);

  return http.response
}

// ajax to set session variable
