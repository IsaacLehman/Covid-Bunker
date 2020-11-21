//scripts go here

// add a listener so that when the document loads . . .
// new listeners  can be attched to elements safely
window.addEventListener("DOMContentLoaded", function() {
  /* SCROLL TO TOP */
  //Get the button
  var topButton = document.getElementById("topBtn");

  // When the user scrolls down 20px from the top of the document, show the button
  window.onscroll = function() {scrollFunction()};

  function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      topButton.style.display = "block";
    } else {
      topButton.style.display = "none";
    }
  }

  const cartButtons = document.querySelectorAll('.add_to_cart');

  cartButtons.forEach(button => {
  	button.addEventListener('click', cartClick);
  });

});

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}

function cartClick() {
	let button = this;
  // add Attribute so when clicked again, nothing happens
  button.setAttribute('disabled', true);
  button.classList.add('cart-clicked');
  // change text
  button.innerHTML = 'Added <i class="fas fa-shopping-cart"></i>';
}
