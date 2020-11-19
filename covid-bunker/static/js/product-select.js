// add a listener so that when the document loads . . .
// new listeners  can be attched to elements safely
window.addEventListener("DOMContentLoaded", function() {

  // get elements
  let face_selector   = document.getElementById('face-mask-selector');
  let hand_selector   = document.getElementById('hand-sanitizer-selector');
  let toilet_selector = document.getElementById('toilet-paper-selector')
  let other_selector  = document.getElementById('other-selector')
  let clear_selector  = document.getElementById('clear-selector')
  let parent_div      = document.getElementById('product-cards');

  // add listeners
  face_selector.addEventListener('click', function() {
    filter(parent_div, 'masks');
  });
  hand_selector.addEventListener('click', function() {
    filter(parent_div, 'hand sanitizer');
  });
  toilet_selector.addEventListener('click', function() {
    filter(parent_div, 'toilet paper');
  });
  other_selector.addEventListener('click', function() {
    filter_other(parent_div);
  });
  clear_selector.addEventListener('click', function() {
    clear_filter(parent_div);
  });

});

function filter(parent, filter_id) {
  var child_divs = parent.children;

  for( i=0; i< child_divs.length; i++ )
  {
     var child_div = child_divs[i];
     var child_id = child_div.firstElementChild.title;

     if (child_id === filter_id) {
       child_div.classList.remove('hidden');
     } else {
       child_div.classList.add('hidden');
     }
  }
}

function filter_other(parent) {
  var child_divs = parent.children;

  for( i=0; i< child_divs.length; i++ )
  {
    var child_div = child_divs[i];
    var child_id = child_div.firstElementChild.title;

     if (child_id === 'masks' || child_id === 'toilet paper' || child_id === 'hand sanitizer') {
       child_div.classList.add('hidden');
     } else {
       child_div.classList.remove('hidden');
     }
  }
}

function clear_filter(parent, filter_id) {
  var child_divs = parent.children;

  for( i=0; i< child_divs.length; i++ )
  {
     var child_div = child_divs[i];
     child_div.classList.remove('hidden');
  }
}
