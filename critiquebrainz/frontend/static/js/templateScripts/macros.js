      $("img").last()
          .on("error", function () {
            $(this).attr("src", "/static/img/missing-art.png");
          })
          .attr("src", "//coverartarchive.org/release-group/{{ entity_id }}/front-250");