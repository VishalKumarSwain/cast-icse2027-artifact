class CategorizedCorpusReaderMixin:
    """
    A mixin class used to aid in the implementation of corpus readers
    for categorized corpora.  This class defines the method
    ``categories()``, which returns a list of the categories for the
    corpus or for a specified set of fileids; and overrides ``fileids()``
    to take a ``categories`` argument, restricting the set of fileids to
    be returned.

    Subclasses are expected to:

      - Call ``__init__()`` to set up the mapping.

      - Override all view methods to accept a ``categories`` parameter,
        which can be used *instead* of the ``fileids`` parameter, to
        select which fileids should be included in the returned view.
    """

    def categories(self, fileids=None):
        if fileids is None:
            return sorted(self._cat_fileids.keys())
        else:
            return sorted(set(self._cat_fileids[fid] for fid in fileids))

    def fileids(self, categories=None):
        if categories is None:
            return super().fileids()
        else:
            return sorted(
                set(
                    fid
                    for fid in self._cat_fileids
                    if self._cat_fileids[fid] in categories
                )
            )
