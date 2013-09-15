# define user types
class UserType(object):

    def __init__(self, label, karma, publications_per_day, rates_per_day):
        self.label = label
        self.karma = karma
        self.publications_per_day = publications_per_day
        self.rates_per_day = rates_per_day

    def is_instance(self, user):
        return self.karma(user.karma)

blocked = UserType(
    label=u'Blocked',
    karma=lambda x: (x < -20),
    publications_per_day=0,
    rates_per_day=0)

spammer = UserType(
    label=u'Spammer',
    karma=lambda x: (x >= -20 and x < -10),
    publications_per_day=1,
    rates_per_day=0)

noob = UserType(
    label=u'Noob',
    karma=lambda x: (x >= -10 and x < 50),
    publications_per_day=5,
    rates_per_day=10)

apprentice = UserType(
    label=u'Apprentice',
    karma=lambda x: (x >= 50 and x < 1000),
    publications_per_day=20,
    rates_per_day=50)

sorcerer = UserType(
    label=u'Sorcerer',
    karma=lambda x: (x >= 1000),
    publications_per_day=50,
    rates_per_day=200)

# register user types
user_types = (blocked, spammer, noob, apprentice, sorcerer)

# define publication classes
class PublicationClass(object):

    def __init__(self, label, rating, upvote, downvote, mark_spam):
        self.label = label
        self.rating = rating
        self.upvote = upvote
        self.downvote = downvote
        self.mark_spam = mark_spam

    def is_instance(self, publication):
        return self.rating(publication.rating)

spam = PublicationClass(
    label=u'Spam',
    rating=lambda x: (x < -10),
    upvote=(apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

neutral = PublicationClass(
    label=u'Neutral',
    rating=lambda x: (x >= -10 and x < 10),
    upvote=(noob, apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

promising = PublicationClass(
    label=u'Promising',
    rating=lambda x: (x >= 10 and x < 30),
    upvote=(spammer, noob, apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

trusted = PublicationClass(
    label=u'Trusted',
    rating=lambda x: (x >= 30),
    upvote=(spammer, noob, apprentice, sorcerer),
    downvote=(apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

# register publication classes
publication_classes = (spam, neutral, promising, trusted)
