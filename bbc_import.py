# This script imports reviews from BBC's MySQL dump into CritiqueBrainz server.
# Note: Before running it, dump has to be imported into local MySQL instance!

# TODO(roman): Create proper importing functionality and integrate it into data package.

from __future__ import print_function
import re
import MySQLdb

from musicbrainzngs import set_useragent, get_release_by_id

import html2text
from ftfy import fix_text
from critiquebrainz.data import db as _db, Review
from critiquebrainz import app
from critiquebrainz.data import User


if __name__ == '__main__':
    _db.app = app

    log = open("import-log.txt", "w")


    # Importing from MySQL database

    print("Importing reviews from MySQL database...")
    set_useragent("BBC importer", 1)

    mydb = MySQLdb.connect(host="localhost", user="root", passwd="root", db="bbc", use_unicode=True)
    cur = mydb.cursor()

    cur.execute("SET NAMES utf8")
    cur.execute("""
        SELECT reviews.release_gid, reviews.url_key, reviews.long_synopsis, reviews.review_date, reviews.updated_at, reviewers.name
        FROM reviews
        JOIN reviewers ON reviews.reviewer_id = reviewers.id
        ORDER BY reviews.id DESC;
        """)

    rows = cur.fetchall()
    count = str(len(rows))
    imported = []
    for i, row in enumerate(rows):
        print("[" + str(i) + "/" + count + "] ")
        if row[0] is None:
            err = "Undefined release id! "
            print(err)
            log.write(err + str(row) + "\n\n")
            continue
        try:
            api_resp = get_release_by_id(row[0], includes=["release-groups"])
            release_group_id = api_resp["release"]["release-group"]["id"]
            user = User.get_or_create(display_name=row[5], musicbrainz_id=None)
            if (release_group_id, user.id) in imported:
                err = "Duplicate review! "
                print(err)
                log.write(err + str(row) + "\n\n")
                continue
            else:
                review = Review.create(user=user,
                                       text=row[2],
                                       release_group=release_group_id,
                                       license_id="CC BY-NC-SA 3.0",
                                       created=row[3],
                                       last_updated=row[4],
                                       source="BBC",
                                       source_url="http://www.bbc.co.uk/music/reviews/" + row[1])
                print((release_group_id, user.display_name))
                imported.append((release_group_id, user.id))
        except Exception as e:
            print(e)
            log.write(str(e) + str(row) + "\n\n")


    # Fixing encoding issues and converting from HTML to Markdown

    # Getting all reviews
    reviews, count = Review.list(None, None, None, None, None)

    print("Converting HTML to Markdown in " + str(count) + " reviews...")

    # Preparing regex stuff
    pattern = re.compile("<a href=\"\/", re.IGNORECASE)
    URL_BEGINNING = "http://www.bbc.co.uk"

    for i, review in enumerate(reviews):
        print("[" + str(i) + "/" + str(count) + "] " + review.id)

        # Fixing encoding
        try:
            review.text = fix_text(review.text)
        except Exception as e:
            print(e)

        # Adding host to links
        iterator = pattern.finditer(review.text)
        current_offset = 0
        for match in iterator:
            pos = match.end() + current_offset - 1  # -1 because we insert before slash
            review.text = review.text[:pos] + URL_BEGINNING + review.text[pos:]
            current_offset += len(URL_BEGINNING)

        # Converting into Markdown
        try:
            converter = html2text.HTML2Text()
            converter.body_width = 0
            # Important to set proper emphasis_mark because some <em> tags have spaces
            # before/after a word, which doesn't work well with '_' character.
            converter.emphasis_mark = '*'
            review.update(text=converter.handle(review.text))
        except Exception as e:
            print(e)


    log.close()
