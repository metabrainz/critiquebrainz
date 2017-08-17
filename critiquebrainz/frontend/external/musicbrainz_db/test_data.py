import datetime
from mbdata.models import (
    LinkPlaceURL,
    LinkType,
    Place,
    PlaceType,
    LinkPlacePlace,
    URL,
    Area,
    Link,
    Artist,
    ArtistCredit,
    ArtistCreditName,
    ArtistType,
    Medium,
    MediumFormat,
    Recording,
    Release,
    ReleaseGroup,
    ReleaseGroupMeta,
    ReleaseGroupPrimaryType,
    ReleaseStatus,
    Script,
    Event,
    EventType,
    Track,
)

# Place (d71ffe38-5eaf-426b-9a2e-e1f21bc84609) with url-rels, place-rels
area_hameenlinna = Area()
area_hameenlinna.id = 9598
area_hameenlinna.gid = '4479c385-74d8-4a2b-bdab-f48d1e6969ba'
area_hameenlinna.name = 'Hämeenlinna'
area_hameenlinna.ended = False
area_hameenlinna.comment = ''

placetype_venue = PlaceType()
placetype_venue.id = 2
placetype_venue.name = 'Venue'
placetype_venue.description = 'A place that has live artistic performances.'
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
linktype_social_network.description = 'A social network description.'
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

# Release (16bee711-d7ce-48b0-adf4-51f124bcc0df) with release group(with its artist credit), medium,
# tracks and recordings
artisttype_person = ArtistType()
artisttype_person.id = 1
artisttype_person.name = 'Person'
artisttype_person.gid = 'b6e035f4-3ce9-331c-97df-83397230b0df'

artist_jay_z = Artist()
artist_jay_z.id = 167
artist_jay_z.gid = 'f82bcf78-5b69-4622-a5ef-73800768d9ac'
artist_jay_z.name = 'JAY Z'
artist_jay_z.sort_name = 'JAY Z'
artist_jay_z.begin_date_year = 1969
artist_jay_z.begin_date_month = 12
artist_jay_z.begin_date_day = 4
artist_jay_z.comment = 'US rapper, formerly Jay-Z'
artist_jay_z.ended = False
artist_jay_z.type = artisttype_person

artistcreditname_jay_z = ArtistCreditName()
artistcreditname_jay_z.position = 0
artistcreditname_jay_z.name = 'Jay-Z'
artistcreditname_jay_z.join_phrase = '/'
artistcreditname_jay_z.artist = artist_jay_z

artisttype_group = ArtistType()
artisttype_group.id = 2
artisttype_group.name = 'Group'
artisttype_group.child_order = 2
artisttype_group.gid = 'e431f5f6-b5d2-343d-8b36-72607fffb74b'

artist_linkin_park = Artist()
artist_linkin_park.id = 11330
artist_linkin_park.gid = 'f59c5520-5f46-4d2c-b2c4-822eabf53419'
artist_linkin_park.name = 'Linkin Park'
artist_linkin_park.sort_name = 'Linkin Park'
artist_linkin_park.begin_date_year = 1995
artist_linkin_park.comment = ''
artist_linkin_park.ended = False
artist_linkin_park.type = artisttype_group

artistcreditname_linkin_park = ArtistCreditName()
artistcreditname_linkin_park.position = 1
artistcreditname_linkin_park.name = 'Linkin Park'
artistcreditname_linkin_park.join_phrase = ''
artistcreditname_linkin_park.artist = artist_linkin_park

artistcredit_jay_z_linkin_park = ArtistCredit()
artistcredit_jay_z_linkin_park.id = 1617798
artistcredit_jay_z_linkin_park.name = 'Jay-Z/Linkin Park'
artistcredit_jay_z_linkin_park.artist_count = 2
artistcredit_jay_z_linkin_park.ref_count = 5
artistcredit_jay_z_linkin_park.created = datetime.datetime(2016, 2, 28, 21, 42, 14, 873583)
artistcredit_jay_z_linkin_park.artists = [
    artistcreditname_jay_z,
    artistcreditname_linkin_park,
]

mediumformat_cd = MediumFormat()
mediumformat_cd.id = 1
mediumformat_cd.name = 'CD'
mediumformat_cd.year = 1982
mediumformat_cd.gid = '9712d52a-4509-3d4b-a1a2-67c88c643e31'

recording_numb_encore_explicit = Recording()
recording_numb_encore_explicit.id = 3094737
recording_numb_encore_explicit.gid = 'daccb724-8023-432a-854c-e0accb6c8678'
recording_numb_encore_explicit.name = 'Numb/Encore (explicit)'
recording_numb_encore_explicit.length = 205280
recording_numb_encore_explicit.comment = ''
recording_numb_encore_explicit.video = False
recording_numb_encore_explicit.artist_credit = artistcredit_jay_z_linkin_park

track_numb_encore_explicit = Track()
track_numb_encore_explicit.id = 20280427
track_numb_encore_explicit.gid = 'dfe024b2-95b2-453f-b03e-3b9fa06f44e6'
track_numb_encore_explicit.position = 1
track_numb_encore_explicit.number = '1'
track_numb_encore_explicit.name = 'Numb/Encore (explicit)'
track_numb_encore_explicit.length = 207000
track_numb_encore_explicit.is_data_track = False
track_numb_encore_explicit.artist_credit = artistcredit_jay_z_linkin_park
track_numb_encore_explicit.recording = recording_numb_encore_explicit

recording_numb_encore_instrumental = Recording()
recording_numb_encore_instrumental.id = 3094739
recording_numb_encore_instrumental.gid = '965b75df-397d-4395-aac8-de11854c4630'
recording_numb_encore_instrumental.name = 'Numb/Encore (instrumental)'
recording_numb_encore_instrumental.length = 207333
recording_numb_encore_instrumental.comment = ''
recording_numb_encore_instrumental.video = False
recording_numb_encore_instrumental.artist_credit = artistcredit_jay_z_linkin_park

track_numb_encore_instrumental = Track()
track_numb_encore_instrumental.id = 20280428
track_numb_encore_instrumental.gid = '4fd6d4b0-0d14-428a-a554-1052060a9a27'
track_numb_encore_instrumental.position = 2
track_numb_encore_instrumental.number = '2'
track_numb_encore_instrumental.name = 'Numb/Encore (instrumental)'
track_numb_encore_instrumental.length = 206000
track_numb_encore_instrumental.is_data_track = False
track_numb_encore_instrumental.artist_credit = artistcredit_jay_z_linkin_park
track_numb_encore_instrumental.recording = recording_numb_encore_instrumental

medium_1 = Medium()
medium_1.id = 1842217
medium_1.position = 1
medium_1.name = ''
medium_1.track_count = 2
medium_1.format = mediumformat_cd
medium_1.tracks = [
    track_numb_encore_explicit,
    track_numb_encore_instrumental,
]

releasegroupprimarytype_single = ReleaseGroupPrimaryType()
releasegroupprimarytype_single.id = 2
releasegroupprimarytype_single.name = 'Single'
releasegroupprimarytype_single.child_order = 2
releasegroupprimarytype_single.gid = 'd6038452-8ee0-3f68-affc-2de9a1ede0b9'

releasegroupmeta = ReleaseGroupMeta()
releasegroupmeta.release_count = 3
releasegroupmeta.first_release_date_year = 2004
releasegroupmeta.rating = 100

releasegroup_numb_encore = ReleaseGroup()
releasegroup_numb_encore.id = 828504
releasegroup_numb_encore.gid = '7c1014eb-454c-3867-8854-3c95d265f8de'
releasegroup_numb_encore.name = 'Numb/Encore'
releasegroup_numb_encore.artist_credit = artistcredit_jay_z_linkin_park
releasegroup_numb_encore.meta = releasegroupmeta
releasegroup_numb_encore.type = releasegroupprimarytype_single

script_latin = Script()
script_latin.id = 28
script_latin.iso_code = 'Latn'
script_latin.iso_number = '215'
script_latin.name = 'Latin'
script_latin.frequency = 4

releasestatus_official = ReleaseStatus()
releasestatus_official.id = 1
releasestatus_official.name = 'Official'
releasestatus_official.description = 'Description for an official release.'
releasestatus_official.gid = '4e304316-386d-3409-af2e-78857eec5cfe'

release_numb_encore = Release()
release_numb_encore.id = 1738247
release_numb_encore.gid = '16bee711-d7ce-48b0-adf4-51f124bcc0df'
release_numb_encore.name = 'Numb/Encore'
release_numb_encore.barcode = '054391612328'
release_numb_encore.comment = ''
release_numb_encore.artist_credit = artistcredit_jay_z_linkin_park
release_numb_encore.mediums = [
    medium_1,
]
release_numb_encore.release_group = releasegroup_numb_encore
release_numb_encore.status = releasestatus_official

track_numb_encore_explicit_1 = Track()
track_numb_encore_explicit_1.id = 7878846
track_numb_encore_explicit_1.gid = '13aa9571-c0a0-3aaf-8159-9511658e5978'
track_numb_encore_explicit_1.position = 1
track_numb_encore_explicit_1.number = '1'
track_numb_encore_explicit_1.name = 'Numb/Encore (explicit)'
track_numb_encore_explicit_1.length = 208253
track_numb_encore_explicit_1.is_data_track = False
track_numb_encore_explicit_1.artist_credit = artistcredit_jay_z_linkin_park
track_numb_encore_explicit_1.recording = recording_numb_encore_explicit

track_numb_encore_instrumental_1 = Track()
track_numb_encore_instrumental_1.id = 7878847
track_numb_encore_instrumental_1.gid = '8f0abcc1-0ec0-3427-9e3e-925ee1e5b3e6'
track_numb_encore_instrumental_1.position = 2
track_numb_encore_instrumental_1.number = '2'
track_numb_encore_instrumental_1.name = 'Numb/Encore (instrumental)'
track_numb_encore_instrumental_1.length = 207453
track_numb_encore_instrumental_1.is_data_track = False
track_numb_encore_instrumental_1.artist_credit = artistcredit_jay_z_linkin_park
track_numb_encore_instrumental_1.recording = recording_numb_encore_instrumental

medium_2 = Medium()
medium_2.id = 527716
medium_2.position = 1
medium_2.name = ''
medium_2.track_count = 2
medium_2.format = mediumformat_cd
medium_2.tracks = [
    track_numb_encore_explicit_1,
    track_numb_encore_instrumental_1,
]

release_numb_encore_1 = Release()
release_numb_encore_1.id = 527716
release_numb_encore_1.gid = 'a64a0467-9d7a-4ffa-90b8-d87d9b41e311'
release_numb_encore_1.name = 'Numb/Encore'
release_numb_encore_1.barcode = '054391612328'
release_numb_encore_1.comment = ''
release_numb_encore_1.quality = -1
release_numb_encore_1.artist_credit = artistcredit_jay_z_linkin_park
release_numb_encore_1.mediums = [
    medium_2,
]
release_numb_encore_1.release_group = releasegroup_numb_encore
release_numb_encore_1.script = script_latin
release_numb_encore_1.status = releasestatus_official

releasegroupmeta_1 = ReleaseGroupMeta()
releasegroupmeta_1.release_count = 4
releasegroupmeta_1.first_release_date_year = 2004

releasegroup_collision_course = ReleaseGroup()
releasegroup_collision_course.id = 1110052
releasegroup_collision_course.gid = '8ef859e3-feb2-4dd1-93da-22b91280d768'
releasegroup_collision_course.name = 'Collision Course'
releasegroup_collision_course.meta = releasegroupmeta_1

eventtype_festival = EventType()
eventtype_festival.id = 2
eventtype_festival.name = 'Festival'
eventtype_festival.description = 'Festival description.'
eventtype_festival.gid = 'b6ded574-b592-3f0e-b56e-5b5f06aa0678'

taubertal_festival_2004 = Event()
taubertal_festival_2004.id = 1607
taubertal_festival_2004.gid = 'ebe6ce0f-22c0-4fe7-bfd4-7a0397c9fe94'
taubertal_festival_2004.name = 'Taubertal-Festival 2004, Day 1'
taubertal_festival_2004.cancelled = False
taubertal_festival_2004.ended = True
taubertal_festival_2004.type = eventtype_festival

eventtype_concert = EventType()
eventtype_concert.id = 1
eventtype_concert.name = 'Concert'
eventtype_concert.description = 'Concert description.'
eventtype_concert.gid = 'ef55e8d7-3d00-394a-8012-f5506a29ff0b'

event_ra_hall_uk = Event()
event_ra_hall_uk.id = 21675
event_ra_hall_uk.gid = '40e6153d-a042-4c95-a0a9-b0a47e3825ce'
event_ra_hall_uk.name = '1996-04-17: Royal Albert Hall, London, England, UK'
event_ra_hall_uk.cancelled = False
event_ra_hall_uk.ended = True
event_ra_hall_uk.type = eventtype_concert

release_collision_course = Release()
release_collision_course.id = 28459
release_collision_course.release_group = releasegroup_collision_course
release_collision_course.gid = 'f51598f5-4ef9-4b8a-865d-06a077bf78cf'
release_collision_course.name = 'Collision Course'
release_collision_course.status = releasestatus_official
