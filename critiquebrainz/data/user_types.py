class UserType(object):

    def __init__(self, label, karma, reviews_per_day, votes_per_day):
        self.label = label
        self.karma = karma
        self.reviews_per_day = reviews_per_day
        self.votes_per_day = votes_per_day

    def is_instance(self, user):
        return self.karma(user.karma)


blocked = UserType(
    label='Blocked',
    karma=lambda x: (x < -20),
    reviews_per_day=0,
    votes_per_day=0)

spammer = UserType(
    label='Spammer',
    karma=lambda x: (x >= -20 and x < -10),
    reviews_per_day=1,
    votes_per_day=0)

noob = UserType(
    label='Noob',
    karma=lambda x: (x >= -10 and x < 50),
    reviews_per_day=5,
    votes_per_day=10)

apprentice = UserType(
    label='Apprentice',
    karma=lambda x: (x >= 50 and x < 1000),
    reviews_per_day=20,
    votes_per_day=50)

sorcerer = UserType(
    label='Sorcerer',
    karma=lambda x: (x >= 1000),
    reviews_per_day=50,
    votes_per_day=200)

user_types = (blocked, spammer, noob, apprentice, sorcerer)
