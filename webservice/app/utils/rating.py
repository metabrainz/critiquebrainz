AMOUNT_PARAM = [100, 10, 1]
RATIO_PARAM = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
RATING_SEQ = [3, 2, 2, 1, 1, 0, 0, 0, -1, -1, -1, -1, -1]
RATING_ARRAY = [RATING_SEQ[0:10], RATING_SEQ[1:11], RATING_SEQ[3:13]]    

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
