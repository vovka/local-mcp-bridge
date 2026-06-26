"""Entrypoint: load config, build the gateway, serve it on :8000/mcp."""
import uvicorn

from bridge.config import Config
from bridge.gateway import build_app


def main() -> None:
    cfg = Config.load()
    print(f"bridge: {len(cfg.upstreams)} upstream(s) -> http://0.0.0.0:8000/mcp")
    uvicorn.run(build_app(cfg), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
