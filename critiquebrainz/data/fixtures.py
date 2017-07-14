import critiquebrainz.db.license as db_license


def install(*args):
    for arg in args:
        if arg == LicenseData:
            for key, entity in arg.__dict__.items():
                if not key.startswith("__"):
                    try:
                        db_license.create(
                            id=entity["id"],
                            full_name=entity["full_name"],
                            info_url=entity["info_url"],
                        )
                    except Exception:
                        print('Failed to add %s!' % key)
                    else:
                        print('Added %s.' % key)


class LicenseData(object):
    """Licenses that can be used with reviews.

    If you add new ones or remove existing, make sure to update forms,
    views, and other stuff that depends on that.
    """
    cc_by_sa_3 = dict(
        id="CC BY-SA 3.0",
        full_name="Creative Commons Attribution-ShareAlike 3.0 Unported",
        info_url="https://creativecommons.org/licenses/by-sa/3.0/",
    )
    cc_by_nc_sa_3 = dict(
        id="CC BY-NC-SA 3.0",
        full_name="Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported",
        info_url="https://creativecommons.org/licenses/by-nc-sa/3.0/",
    )


# Include all objects into this tuple.
all_data = (LicenseData, )
