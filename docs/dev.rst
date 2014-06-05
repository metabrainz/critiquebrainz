Development
===========

Modifying strings in client
---------------------------

CritiqueBrainz Client supports interface translation. If you add or modify strings that will be displayed to user,
you need to wrap them in one of two functions: ``gettext()`` or ``ngettext()``.

Before committing changes don't forget to extract all strings into ``messages.pot``.

For more info see :doc:`translation`.
