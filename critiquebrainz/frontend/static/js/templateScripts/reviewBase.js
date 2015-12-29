    $(document).ready(function() {
      // Show warning when leaving review editor without saving changes
      var beingSaved = false;
      var oldData = $('#review-editor').serialize();
      $(window).bind('beforeunload', function(e) {
        if (beingSaved || (oldData == $('#review-editor').serialize())) {
          return undefined;
        }
        var confirmationMessage = "Your review has not been saved.";
        (e || window.event).returnValue = confirmationMessage;     // Gecko and Trident
        return confirmationMessage;                                // Gecko and WebKit
      });

      $("#btn-publish").click(function(){
        beingSaved = true;
        $("#state").attr('value', 'publish');
        $("#review-editor").submit();
      });
      if ('{{not review or review.is_draft}}'){
        $("#btn-draft").click(function(){
          beingSaved = true;
          $("#state").attr('value', 'draft');
          $("#review-editor").submit();
        });
      }
      // Preview tab functionality
      $(function() {
        $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
          if (e.target.hash.substring(1) == "preview") {
            var text = $("#review-content").val();
            if (!text) {
              $("#preview").html('<em class="text-muted">' + "{{ _('Review is empty.') | tojson }}" + '</em>');
            } else {
              $.ajax({
                type: "POST",
                url: "{{ url_for('review.preview') }}",
                data: { text: text },
                success: function(data) { $("#preview").html(data); },
                error: function() { $("#preview").html('<em class="text-danger">' + "{{ _('Failed to load preview.') | tojson }}" + '</em>'); }
              });
            }
          } else {
            $("#preview").html('<em class="text-muted">' + "{{ _('Loading preview...') | tojson }}" + '</em>');
          }
        });
      });
    });
