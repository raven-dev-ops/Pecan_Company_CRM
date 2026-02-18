from __future__ import annotations

from pathlib import Path

from pecan_crm.config.env_parser import parse_env_file


def test_parse_env_file_ignores_comments_and_blank_lines(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n"
        "\n"
        "A=1\n"
        "B = two\n"
        "INVALID_LINE\n"
        "C='three'\n",
        encoding="utf-8",
    )

    parsed = parse_env_file(env_file)

    assert parsed["A"] == "1"
    assert parsed["B"] == "two"
    assert parsed["C"] == "three"
    assert "INVALID_LINE" not in parsed


def test_parse_env_file_missing_returns_empty(tmp_path: Path) -> None:
    parsed = parse_env_file(tmp_path / "missing.env")
    assert parsed == {}