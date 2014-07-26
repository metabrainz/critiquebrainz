from flask.ext.babel import gettext

# USER TYPES
class UserType(object):

    def __init__(self, label, karma, reviews_per_day, votes_per_day):
        self.label = label
        self.karma = karma
        self.reviews_per_day = reviews_per_day
        self.votes_per_day = votes_per_day

    def is_instance(self, user):
        return self.karma(user.karma)

blocked = UserType(
    label=gettext('Blocked'),
    karma=lambda x: (x < -20),
    reviews_per_day=0,
    votes_per_day=0)

spammer = UserType(
    label=gettext('Spammer'),
    karma=lambda x: (x >= -20 and x < -10),
    reviews_per_day=1,
    votes_per_day=0)

noob = UserType(
    label=gettext('Noob'),
    karma=lambda x: (x >= -10 and x < 50),
    reviews_per_day=5,
    votes_per_day=10)

apprentice = UserType(
    label=gettext('Apprentice'),
    karma=lambda x: (x >= 50 and x < 1000),
    reviews_per_day=20,
    votes_per_day=50)

sorcerer = UserType(
    label=gettext('Sorcerer'),
    karma=lambda x: (x >= 1000),
    reviews_per_day=50,
    votes_per_day=200)

user_types = (blocked, spammer, noob, apprentice, sorcerer)


# REVIEW CLASSES
class ReviewClass(object):

    def __init__(self, label, rating, upvote, downvote, mark_spam):
        self.label = label
        self.rating = rating
        self.upvote = upvote
        self.downvote = downvote
        self.mark_spam = mark_spam

    def is_instance(self, review):
        return self.rating(review.rating)

spam = ReviewClass(
    label=gettext('Spam'),
    rating=lambda x: (x < -10),
    upvote=(apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

neutral = ReviewClass(
    label=gettext('Neutral'),
    rating=lambda x: (x >= -10 and x < 10),
    upvote=(noob, apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

promising = ReviewClass(
    label=gettext('Promising'),
    rating=lambda x: (x >= 10 and x < 30),
    upvote=(spammer, noob, apprentice, sorcerer),
    downvote=(noob, apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

trusted = ReviewClass(
    label=gettext('Trusted'),
    rating=lambda x: (x >= 30),
    upvote=(spammer, noob, apprentice, sorcerer),
    downvote=(apprentice, sorcerer),
    mark_spam=(apprentice, sorcerer))

review_classes = (spam, neutral, promising, trusted)
