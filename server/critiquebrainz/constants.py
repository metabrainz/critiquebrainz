# define user types
noob = dict(
    label='Noob',
    karma=None,
    publications_per_day=5,
    rates_per_day=10)

apprentice = dict(
    label='Apprentice',
    karma=50,
    publications_per_day=20,
    rates_per_day=50)

sorcerer = dict(
    label='Sorcerer',
    karma=1000,
    publications_per_day=50,
    rates_per_day=200)

# register user types
user_types = (sorcerer, apprentice, noob)
