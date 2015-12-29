        L.Icon.Default.imagePath = '/static/img/';
        var map = L.map('map').setView(['{{ lat }}', '{{ long }}'], 14);
        var s = '{{s}}', z = '{{z}}', x = '{{x}}', y = '{{y}}';
        L.tileLayer(`http://${s}.tile.openstreetmap.org/${z}/${x}/${y}.png`,
          {
            attribution: '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
          }).addTo(map);

        var popup = L.popup()
          .setContent("<b>" + '{{ _("Held At") | tojson }}' + "</b><br> " + '{{ place["name"] | tojson }}');

        var marker = L.marker(['{{ lat }}', '{{ long }}'])
          .addTo(map)
          .bindPopup(popup)
          .openPopup();
