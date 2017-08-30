$(document).ready(function() {
  $("#only-reviewed").change(function() {
    if($('#only-reviewed').is(":checked")) {
      $(".not_reviewed").hide();
      var reviewed = $('.reviewed').length;
      var release_group_count = $('.release-group').length;
      if(reviewed == 0 && release_group_count != 0) {
          $("#no-reviewed-entities").removeClass('hidden');
      }
    }
    else {
      $(".not_reviewed").show();
      $("#no-reviewed-entities").addClass('hidden');
    }
  })
})
