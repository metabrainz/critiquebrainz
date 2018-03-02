from mbdata import models

# Unknown entities
unknown_artist = models.Artist()
unknown_artist.gid = '125ec42a-7229-4250-afc5-e057484327fe'
unknown_artist.id = 97546
unknown_artist.name = '[unknown]'
unknown_artist.sort_name = '[unknown]'

unknown_artist_credit_name = models.ArtistCreditName()
unknown_artist_credit_name.name = '[unknown]'
unknown_artist_credit_name.artist = unknown_artist

unknown_artist_credit = models.ArtistCredit()
unknown_artist_credit.name = '[unknown]'
unknown_artist_credit.artists = [unknown_artist_credit_name]

unknown_release_group = models.ReleaseGroup()
unknown_release_group.artist_credit = unknown_artist_credit
unknown_release_group.id = 0
unknown_release_group.name = '[Unknown Release Group]'

unknown_place = models.Place()
unknown_place.id = 0
unknown_place.name = '[Unknown Place]'

unknown_event = models.Place()
unknown_event.id = 0
unknown_event.name = '[Unknown Event]'
