"""Per-source parser modules.

Naming convention: `scripts/parsers/<source-slug>_<vintage>.py`. Each
module exposes ``parse(path: Path) -> pandas.DataFrame``, returning a
frame whose columns include `LONG_COLUMNS` from `scripts.schema`.

For long-running series where upstream layouts change, split per
vintage band: `boulder_sov_2009.py`, `boulder_sov_2015_present.py`.
The `Source.ingest()` method in `scripts/sources.py` dispatches on
`artifact.vintage`.

See `references/project-template.md` for the per-source layout and
`references/toolchain-pdf.md`, `toolchain-tabular.md` etc. for the
per-format extraction patterns.
"""
