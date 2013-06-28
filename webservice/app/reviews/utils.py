from models import Vote
from constants import *

def compute_rating(overall, positive):
    """ Compute the rating """
    try:
        ratio = float(positive)/float(overall)
    except ZeroDivisionError:
        return 0

    for i in xrange(len(AMOUNT_PARAM)):
        if overall >= AMOUNT_PARAM[i]:
            break
                
    for j in xrange(len(RATIO_PARAM)):
        if ratio >= RATIO_PARAM[j]:
            break
                
    return RATING_ARRAY[i][j]
