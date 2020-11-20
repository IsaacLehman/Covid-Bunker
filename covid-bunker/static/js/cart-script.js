

// add a listener so that when the document loads . . .
// new listeners  can be attched to elements safely
window.addEventListener("DOMContentLoaded", function() {
  let add_to_cart_buttons = document.querySelectorAll('.add_to_cart');
  for (var i = 0; i < add_to_cart_buttons.length; i++) {
    add_to_cart_buttons[i].addEventListener('click', function(e) {
      // get the VALUE
      let pid = e.target.value;
      ajax_add_to_cart(pid);
    });
  }

  // set num items in cart
  ajax_update_cart()
});



function get_num_items_in_cart(cart) {
    let num = 0;
    for (i = 0; i < cart.length; i++) {
      num += cart[i].quantity;
    }
    return num;
}

function updateCartNumber(num_items_in_cart) {
  let car_nav_link = document.getElementById('cart-nav');
  let icon = '<i class="fas fa-shopping-cart"></i>'
  let updated_text = icon + ' Cart ' + num_items_in_cart;
  car_nav_link.innerHTML = updated_text;
}

function ajax_update_cart() {
  path = '/ajax_get_cart/'; // where to send the request
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      updateCartNumber(get_num_items_in_cart(cart));
    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened');
    }
  }

  http.open('GET', path, true); // asynchronus ajax_request
  http.send();
}

// clears the cart
function ajax_remove_product_from_cart(pID) {
  path = '/ajax_add_to_cart/'; // where to send the request
  request = 'pid=' + pID;
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      let num_items_in_cart = get_num_items_in_cart(cart);
      updateCartNumber(num_items_in_cart);

    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened', http.responseText);
    }
  }

  http.open('POST', path, true); // asynchronus ajax_request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.send(request);
}

// executes a request to a given path and returns the response
function ajax_add_to_cart(pID) {
  path = '/ajax_add_to_cart/'; // where to send the request
  request = 'pid=' + pID;
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      let num_items_in_cart = get_num_items_in_cart(cart);
      updateCartNumber(num_items_in_cart);

    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened', http);
    }
  }

  http.open('POST', path, true); // asynchronus ajax_request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.send(request);
}

// ajax to set session variable
