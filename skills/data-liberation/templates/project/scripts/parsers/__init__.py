"""Parser modules: one per layout era of the source.

Name them `<source>_<era>.py` (`example_2009_2014.py`, `example_2015_present.py`),
or `<source>.py` when the layout never changed, and route to them explicitly in
`scripts/source.py:parser_for`. Each module exposes:

    METHOD = "text_layer"        # canonical extraction_method (see provenance.py)
    TOOLS = ("pypdfium2",)       # distributions whose versions land in provenance.csv
    QUALITY = "clean"            # optional: "caveats" when the method is known lossy
    NOTES = ""                   # optional: what a user should know about this era

    def parse(path: Path) -> pandas.DataFrame: ...

`parse` returns at least the columns in `scripts.schema.LONG_COLUMNS` other than
`source` and `vintage`, which `clean` fills in. It may keep a `page` column (or a
URL and selector) so each value traces to where it was read. Keep text extraction
separate from line parsing (text lines in, rows out) so the PDF engine can change
without touching the parsing logic. Raise on anything unexpected: `clean` records
the failure and carries on with the other artifacts.

Each parser gets a small real fixture under `tests/fixtures/` and a test that
checks a printed total from it.
"""
