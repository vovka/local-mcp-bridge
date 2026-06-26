FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Node + the official filesystem MCP server (an upstream the bridge spawns).
RUN apt-get update \
 && apt-get install -y --no-install-recommends nodejs npm \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g @modelcontextprotocol/server-filesystem chrome-devtools-mcp \
 && rm -rf /root/.npm

# Install deps from pyproject only (code is mounted in dev / COPYed in prod).
COPY pyproject.toml ./
COPY bridge ./bridge
RUN pip install --no-cache-dir .

CMD ["python", "-m", "bridge"]
