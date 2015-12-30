if ('{{"count"}}' > "{{'limit'}}"){
  var current_page = 0;
  function load_more() {
    var more_button = $("#more-button");
    var loading_message = $("#loading-message");
    more_button.hide();
    loading_message.show();
    $.ajax({
      url: "{{ url_for('reports.more') }}",
      data: { page: ++current_page }
    })
    .done(function(data) {
      loading_message.hide();
      $("#results").append(data.results);
      if (data.more === true) more_button.show();
    })
    .fail(function() {
      alert('{{ _("Failed to load older reports!") | tojson }}');
    });
  }
}
// Display a modal to confirm the action
$('.confirm-first').on('click', function(e){
  e.preventDefault();

  // Set the data for action
  var href = $(this).attr('href');
  var text = $(this).attr('data-confirm-text');
  $('#confirm-modal').find('.btn-danger').attr('href', href);
  $('#confirm-modal').find('.modal-body').text(text);

  // Display the modal
  $('#confirm-modal').modal();
});
