$(document).ready(function() {
  var page = 0, releaseGroups, totalPages, limit=20;
  releaseGroups = $('.release-group');
  showReleaseGroups(releaseGroups);

  $("#only-reviewed").change(function() {
    if($('#only-reviewed').is(":checked")) {
      if(!$('.has-review').length){
        $('#no-reviewed-entities').removeClass('hidden');
      }
      showReleaseGroups('.has-review');
    }
    else {
      $('#no-reviewed-entities').addClass('hidden');
      showReleaseGroups('.release-group');
    }
  });

  $('.nextLink').click(function(link) {
    link.preventDefault();
    changePage(page, 1);
    if(page === 0){
      $('.previous').removeClass('hidden');
    }
    page += 1;
    if(page === totalPages - 1) {
      $('.next').addClass('hidden');
    }
  });

  $('.previousLink').click(function(link) {
    link.preventDefault();
    changePage(page, -1);
    if(page === totalPages - 1) {
      $('.next').removeClass('hidden');
    }
    page -= 1;
    if(page === 0) {
      $('.previous').addClass('hidden');
    }
  });

  function showReleaseGroups(className) {
    releaseGroups = $(className);
    totalPages = Math.floor(releaseGroups.length / 20);
    if(releaseGroups.length % 20) {
      totalPages += 1;
    }
    page = 0;
    $('.release-group').addClass('hidden');
    $('.previous').addClass('hidden');
    if(totalPages <= 1) {
      $('.next').addClass('hidden');
    } else {
      $('.next').removeClass('hidden');
    }
    changePage(page, 0);
  }

  function changePage(current, change) {
    var prev = releaseGroups.slice(current*limit, current*limit + limit);
    var cur = releaseGroups.slice((current+change)*limit, (current+change)*limit + limit);
    if(change){
      [].forEach.call(prev, function(element) {
        $(element).addClass('hidden');
      });
    }
    [].forEach.call(cur, function(element) {
      $(element).removeClass('hidden');
    });
  }
})
