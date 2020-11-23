

// add a listener so that when the document loads . . .
// new listeners  can be attched to elements safely
window.addEventListener("DOMContentLoaded", function() {
  let add_to_cart_buttons = document.querySelectorAll('.add_to_cart');
  for (var i = 0; i < add_to_cart_buttons.length; i++) {
    add_to_cart_buttons[i].addEventListener('click', function(e) {
      // add click anamation
      this.classList.add('clicked');

      // get the VALUE
      let pid = e.target.value;

      // get the quantity selected (if available)
      let quantity = 1;
      let quantity_selector = document.getElementById(`quantity-select-${pid}`);
      if (quantity_selector != null) {
          quantity = quantity_selector.value;
          console.log('value', quantity);
      }

      ajax_add_to_cart(pid, quantity);
    });
  }

  let remove_from_cart_buttons = document.querySelectorAll('.remove_from_cart');
  for (var i = 0; i < remove_from_cart_buttons.length; i++) {
    remove_from_cart_buttons[i].addEventListener('click', function(e) {
      // get the pID VALUE
      let pid = e.target.value;
      ajax_remove_from_cart(pid);
    });
  }

  // set num items in cart
  ajax_update_cart()
});


/* -------------------------------------------------------------------------- */
/*                                FUNCTIONS                                   */
/* -------------------------------------------------------------------------- */
// format into currency
const formatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  minimumFractionDigits: 2
})

function get_num_items_in_cart(cart) {
    let num = 0;
    if(cart != null) { // if there are items in cart
      for (i = 0; i < cart.length; i++) {
        num += cart[i].quantity;
      }
    }
    return num;
}

function get_cart_total(cart) {
    let total_price = 0.0;
    if(cart != null) { // if there are items in cart
      for (i = 0; i < cart.length; i++) {
        total_price += cart[i].price;
      }
    }
    return total_price;
}

function set_cart_total(cart) {
  let total_holder = document.getElementById('cart-icon-cart-page');
  if (total_holder == null) {
    return;
  }
  let cart_text = '<i class="fas fa-shopping-cart"></i> Total';

  let total_price = get_cart_total(cart);

  if (total_price <= 0) {
    let top_btn = document.getElementById('top-buy-now-btn');
    let bot_btn = document.getElementById('bottom-cart-btns');

    if (top_btn != null) {
      top_btn.remove();
    }

    if (bot_btn != null) {
      bot_btn.remove();
    }

    total_holder.innerHTML = cart_text;
  } else {
    total_holder.innerHTML = cart_text + ' - ' + formatter.format(total_price);
  }
}

function updateCartNumber(num_items_in_cart) {
  let car_nav_link = document.getElementById('cart-nav');
  let icon = '<i class="fas fa-shopping-cart"></i>'
  if (num_items_in_cart > 0) {
    let updated_text = icon + ' Cart ' + num_items_in_cart;
    car_nav_link.innerHTML = updated_text;
  } else {
    let updated_text = icon + ' Cart ';
    car_nav_link.innerHTML = updated_text;
  }
}

/* -------------------------------------------------------------------------- */
/*                           UPDATE CART NUMBER                               */
/* -------------------------------------------------------------------------- */
function ajax_update_cart() {
  path = '/ajax_get_cart/'; // where to send the request
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      updateCartNumber(get_num_items_in_cart(cart));
      set_cart_total(cart);
    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened');
    }
  }

  http.open('GET', path, true); // asynchronus ajax_request
  http.send();
}

/* -------------------------------------------------------------------------- */
/*                           REMOVE FROM CART                                 */
/* -------------------------------------------------------------------------- */
// removes a product from the cart
function ajax_remove_from_cart(pID) {
  path = '/ajax_remove_item_from_cart/'; // where to send the request
  request = 'pid=' + pID;
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      let num_items_in_cart = get_num_items_in_cart(cart);
      updateCartNumber(num_items_in_cart);
      set_cart_total(cart);

      // remove product from page
      document.getElementById(pID).remove();


    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened', http.responseText);
    }
  }

  http.open('POST', path, true); // asynchronus ajax_request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.send(request);
}

/* -------------------------------------------------------------------------- */
/*                              ADD TO CART                                   */
/* -------------------------------------------------------------------------- */
// executes a request to a given path and returns the response
function ajax_add_to_cart(pID, quantity) {
  path = '/ajax_add_to_cart/'; // where to send the request
  request = `pid=${pID}&quantity=${quantity}`;//'pid=' + pID;
  let http = new XMLHttpRequest();

  http.onreadystatechange = function(){
    if(http.readyState == 4 && http.status == 200) {
      // what to do if response was good
      let cart = JSON.parse(http.response);
      let num_items_in_cart = get_num_items_in_cart(cart);
      updateCartNumber(num_items_in_cart);

    } else if(http.readyState == 4 && http.status != 200)  {
      // what to do if bad response
      console.log('bad ajax happened', http.responses);
    }
  }

  http.open('POST', path, true); // asynchronus ajax_request
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  http.send(request);
}

// ajax to set session variable
