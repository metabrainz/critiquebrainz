      var current_page = 0;
      function load_more() {
        var more_button = $("#more-button");
        var loading_message = $("#loading-message");
        more_button.hide();
        loading_message.show();
        $.ajax({
          url: "{{ url_for('log.more') }}",
          data: { page: ++current_page }
        })
        .done(function(data) {
          loading_message.hide();
          $("#results").append(data.results);
          if (data.more === true) more_button.show();
        })
        .fail(function() {
          alert('{{ _("Failed to load older logs!") | tojson }}');
        });
      }
