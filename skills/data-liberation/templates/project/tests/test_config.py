"""A long run can point every data path at a copy of data/ outside the repository."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

import scripts.config


@pytest.fixture
def config_with_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(scripts.config.DATA_DIR_ENV, str(tmp_path / "copy"))
    yield importlib.reload(scripts.config)
    monkeypatch.delenv(scripts.config.DATA_DIR_ENV)
    importlib.reload(scripts.config)


def test_default_data_dir_is_in_the_repository() -> None:
    assert scripts.config.DATA == scripts.config.ROOT / "data"


def test_data_dir_override_moves_every_data_path(config_with_data_dir, tmp_path) -> None:
    cfg = config_with_data_dir
    assert cfg.DATA == (tmp_path / "copy").resolve()
    for path in (cfg.DATA_ORIGINAL, cfg.DATA_PROCESSED, cfg.DATA_AUDIT, cfg.PROCESSED_CSV):
        assert cfg.DATA in path.parents
    assert cfg.DOCS == cfg.ROOT / "docs"  # docs stay in the working tree


def test_display_path_reads_like_the_repository(config_with_data_dir) -> None:
    cfg = config_with_data_dir
    assert cfg.display_path(cfg.PROCESSED_CSV) == Path("data/processed") / cfg.PROCESSED_CSV.name
    assert cfg.display_path(cfg.ROOT / "README.md") == Path("README.md")
