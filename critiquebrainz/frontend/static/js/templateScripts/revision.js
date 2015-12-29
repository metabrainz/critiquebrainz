    $(document).ready(function() {
      $("input[name=new]:nth(0)").attr('checked', true);
      $("input[name=old]:nth(1)").attr('checked', true);

      $("#btn-compare").click(function(event){
        var old_val = $('input[name=old]:checked').val();
        var new_val = $('input[name=new]:checked').val();
        if (old_val == new_val) {
          alert("{{ _('Select two different revisions.') | tojson }}");
          event.preventDefault();
        } else {
          $("#review-compare").submit();
        }
      });

      if ('{{"count"}}' > '{{"limit"}}')
        var current_page = 0;
        function load_more() {
          var more_button = $("#more-button");
          var loading_message = $("#loading-message");
          more_button.hide();
          loading_message.show();
          $.ajax({
            url: "{{ url_for('review.revisions_more', id=review.id) }}",
            data: { page: ++current_page }
          })
          .done(function(data) {
            loading_message.hide();
            $("#results").append(data.results);
            if (data.more === true) more_button.show();
          })
          .fail(function() {
            alert('{{ _("Failed to load older revisions!") | tojson }}');
          });
        }
    });