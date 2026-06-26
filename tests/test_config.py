"""Self-check (no pytest): python tests/test_config.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bridge.config import Config


def _cfg(text: str) -> str:
    path = os.path.join(tempfile.mkdtemp(), "c.yaml")
    with open(path, "w") as f:
        f.write(text)
    return path


def test_fail_closed_without_token() -> None:
    os.environ.pop("BRIDGE_TOKEN", None)
    try:
        Config.load(_cfg("upstreams: []"))
    except SystemExit:
        return
    raise AssertionError("expected SystemExit when BRIDGE_TOKEN is unset")


def test_parses_upstreams_and_allowlist() -> None:
    os.environ["BRIDGE_TOKEN"] = "x"
    cfg = Config.load(_cfg("upstreams:\n  - name: b\n    command: npx\nallowlist: [b.go]\n"))
    assert cfg.upstreams[0].command == "npx"
    assert cfg.allowlist == ["b.go"]


if __name__ == "__main__":
    test_fail_closed_without_token()
    test_parses_upstreams_and_allowlist()
    print("ok")
