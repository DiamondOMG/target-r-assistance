# Jarvis MCP Server

Python MCP server exposing read-only query operations over the Target-R data synced to Neon.

## Setup

From this directory, create a virtual environment, install the package, and copy `.env.example` to `.env` or configure the variables in the process environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

Set `NEON_FUNCTION_URL` and `NEON_MANUAL_SYNC_TOKEN` in the environment. Do not commit `.env` or expose the token to an Agent or Model. The server requires HTTPS for the Neon Function URL.

Run the server over stdio:

```bash
jarvis-mcp
```

Or:

```bash
python -m jarvis_mcp.server
```

## Tool

`targetr_query` supports `screen`, `sequence`, and `libraryitem` with `count`, `select`, and `group_count`. Fields/operators are allowlisted; `select` requires an explicit field list. Results are filtered and projected in the MCP process; raw JSONB `data` is rejected and never returned.

`targetr_function` processes raw Neon table JSON inside MCP and, by default, writes all matching rows and source fields (including nested raw JSON as JSON text) to a CSV file. It returns the local file path, not the dataset in the tool response. Filters, projection, sorting, aggregation and optional limit/offset are supported. No hard cap is imposed on row count or CSV size; large exports require sufficient MCP-host memory and disk. See `TOOLS/targetr_function.md`.

The server caches each entity in memory for `TARGETR_CACHE_TTL_SECONDS` (default 120 seconds). Cache is process-local and is cleared when the MCP server restarts. A cache miss or expiry fetches the non-raw Neon endpoint; it does not sync Target-R. Use `freshness="refresh"` only when latest data is needed: this calls the corresponding Neon sync endpoint, waits `TARGETR_REFRESH_WAIT_SECONDS` (default 1 second), then fetches the non-raw dataset again. Refresh performs a write/upsert in the Neon database as part of the existing sync process.

The Neon endpoints currently return all rows per request. This implementation intentionally filters after fetching all non-raw rows, as agreed for the initial small-user deployment.

## Tests

```bash
python -m pytest
```
