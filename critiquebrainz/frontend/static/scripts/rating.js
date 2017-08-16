require('bootstrap-rating-input');

$.fn.rating.Constructor.DEFAULTS.clearable = '';
$.fn.rating.Constructor.DEFAULTS.clearableIcon = 'glyphicon-remove-circle';

$(document).ready(function() {
  // Set color and size of stars icon
  $('.glyphicon-star, .glyphicon-star-empty').css({'color': '#DAA520', 'font-size': '18px'});
  // Set color and size of delete icon
  $('.glyphicon-remove-circle').css({'color': '#808080', 'font-size': '16px'});
  $('.glyphicon-remove-circle').hover(function() {
    $(this).css('color', 'red');
    }, function() {
    $(this).css('color', '#808080');
    });
  $('.glyphicon-remove-circle').attr('title', 'Delete');
});