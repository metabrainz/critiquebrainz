import datetime
from mbdata.models import LinkPlaceURL, LinkType, Place, PlaceType, LinkPlacePlace, URL, Area, Link

area_hameenlinna = Area()
area_hameenlinna.id = 9598
area_hameenlinna.gid = '4479c385-74d8-4a2b-bdab-f48d1e6969ba'
area_hameenlinna.name = 'Hämeenlinna'
area_hameenlinna.ended = False
area_hameenlinna.comment = ''

placetype_venue = PlaceType()
placetype_venue.id = 2
placetype_venue.name = 'Venue'
placetype_venue.description = 'A place that has live artistic performances as one of its primary functions, such as a concert hall.'
placetype_venue.gid = 'cd92781a-a73f-30e8-a430-55d7521338db'

place_suisto = Place()
place_suisto.id = 955
place_suisto.gid = 'd71ffe38-5eaf-426b-9a2e-e1f21bc84609'
place_suisto.name = 'Suisto'
place_suisto.address = 'Verkatehtaankuja 7, FI-13200 Hämeenlinna, Finland'
place_suisto.coordinates = (60.997758, 24.477142)
place_suisto.comment = ''
place_suisto.begin_date_year = 2009
place_suisto.ended = False
place_suisto.area = area_hameenlinna
place_suisto.type = placetype_venue

url_1 = URL()
url_1.id = 2003126
url_1.gid = '7462ea62-7439-47f7-93bc-a425d1d989e8'
url_1.url = 'http://www.suisto.fi/'

linktype_official_homepage = LinkType()
linktype_official_homepage.id = 363
linktype_official_homepage.gid = '696b79da-7e45-40e6-a9d4-b31438eb7e5d'
linktype_official_homepage.entity_type0 = 'place'
linktype_official_homepage.entity_type1 = 'url'
linktype_official_homepage.name = 'official homepage'
linktype_official_homepage.description = 'Indicates the official homepage for a place.'
linktype_official_homepage.link_phrase = 'official homepages'
linktype_official_homepage.reverse_link_phrase = 'official homepage for'
linktype_official_homepage.long_link_phrase = 'has an official homepage at'
linktype_official_homepage.is_deprecated = False
linktype_official_homepage.has_dates = True
linktype_official_homepage.entity0_cardinality = 0
linktype_official_homepage.entity1_cardinality = 0

link_3 = Link()
link_3.id = 133735
link_3.attribute_count = 0
link_3.created = datetime.datetime(2013, 10, 17, 14, 56, 42, 321443)
link_3.ended = False
link_3.link_type = linktype_official_homepage

linkplaceurl_1 = LinkPlaceURL()
linkplaceurl_1.id = 502
linkplaceurl_1.link_order = 0
linkplaceurl_1.entity0 = place_suisto
linkplaceurl_1.entity1 = url_1
linkplaceurl_1.entity0_id = place_suisto.id
linkplaceurl_1.entity1_id = url_1.id
linkplaceurl_1.link = link_3

url_2 = URL()
url_2.id = 2003133
url_2.gid = '8de22e00-c8e8-475f-814e-160ef761da63'
url_2.url = 'https://twitter.com/Suisto'

linktype_social_network = LinkType()
linktype_social_network.id = 429
linktype_social_network.child_order = 0
linktype_social_network.gid = '040de4d5-ace5-4cfb-8a45-95c5c73bce01'
linktype_social_network.entity_type0 = 'place'
linktype_social_network.entity_type1 = 'url'
linktype_social_network.name = 'social network'
linktype_social_network.description = 'A social network page is a place\'s own page on a <a href="https://en.wikipedia.org/wiki/Social_networking_service">social network</a> which only people involved with the place can post content to. Examples include Facebook pages, and accounts on Twitter, Instagram and Flickr.'
linktype_social_network.link_phrase = 'social networking'
linktype_social_network.reverse_link_phrase = 'social networking page for'
linktype_social_network.long_link_phrase = 'has a social networking page at'
linktype_social_network.is_deprecated = False
linktype_social_network.has_dates = True
linktype_social_network.entity0_cardinality = 0
linktype_social_network.entity1_cardinality = 0

link_4 = Link()
link_4.id = 133745
link_4.attribute_count = 0
link_4.created = datetime.datetime(2013, 10, 17, 15, 6, 28, 583800)
link_4.ended = False
link_4.link_type = linktype_social_network

linkplaceurl_2 = LinkPlaceURL()
linkplaceurl_2.id = 507
linkplaceurl_2.entity0 = place_suisto
linkplaceurl_2.entity1 = url_2
linkplaceurl_2.entity0_id = place_suisto.id
linkplaceurl_2.entity1_id = url_2.id
linkplaceurl_2.link = link_4

place_verkatehdas = Place()
place_verkatehdas.id = 734
place_verkatehdas.gid = 'f9587914-8505-4bd1-833b-16a3100a4948'
place_verkatehdas.name = 'Verkatehdas'
place_verkatehdas.address = 'Paasikiventie 2, FI-13200 Hämeenlinna, Finland'
place_verkatehdas.coordinates = (60.99727, 24.47651)
place_verkatehdas.comment = ''
place_verkatehdas.ended = False
place_verkatehdas.area = area_hameenlinna
place_verkatehdas.type = placetype_venue

linktype_parts = LinkType()
linktype_parts.id = 717
linktype_parts.child_order = 0
linktype_parts.gid = 'ff683f48-eff1-40ab-a58f-b128098ffe92'
linktype_parts.entity_type0 = 'place'
linktype_parts.entity_type1 = 'place'
linktype_parts.name = 'parts'
linktype_parts.description = 'This indicates that a place is part of another place.'
linktype_parts.link_phrase = 'parts'
linktype_parts.reverse_link_phrase = 'part of'
linktype_parts.long_link_phrase = 'has part'
linktype_parts.is_deprecated = False
linktype_parts.has_dates = True

link_1 = Link()
link_1.id = 138113
link_1.attribute_count = 0
link_1.ended = False
link_1.link_type = linktype_parts

linkplaceplace_1 = LinkPlacePlace()
linkplaceplace_1.id = 47
linkplaceplace_1.link_order = 0
linkplaceplace_1.entity0_credit = ''
linkplaceplace_1.entity1_credit = ''
linkplaceplace_1.entity0 = place_verkatehdas
linkplaceplace_1.entity1 = place_suisto
linkplaceplace_1.link = link_1
