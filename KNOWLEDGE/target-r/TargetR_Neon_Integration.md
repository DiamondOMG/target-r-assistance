# Target-R Neon integration

Neon project `plain-voice-39403628`, branch `production` (`br-patient-morning-b3iz9oy8`), database `neondb`.

## Services and API

One Neon Function, slug `syncscreens`, serves the manual sync, daily schedule call, and authenticated table-read API.

Base URL:

```text
https://br-patient-morning-b3iz9oy8-syncscreens.compute.c-4.ap-southeast-1.aws.neon.tech/
```

All service calls use `Authorization: Bearer <MANUAL_SYNC_TOKEN>`, except Neon schedule calls, which are authenticated by Neon’s `X-Neon-Trigger-Invocation-Id` header and schedule payload.

### Manual sync

```http
POST /sync
Authorization: Bearer <MANUAL_SYNC_TOKEN>
```

Success response: `{"ok":true,"synced":4299}` (the count varies). `POST /` remains supported for compatibility.

```bash
curl -X POST "$FUNCTION_URL/sync" \\
  -H "Authorization: Bearer $MANUAL_SYNC_TOKEN"
```

### List public base tables

```http
GET /tables
Authorization: Bearer <MANUAL_SYNC_TOKEN>
```

Returns table names in the `public` schema.

```bash
curl "$FUNCTION_URL/tables" \\
  -H "Authorization: Bearer $MANUAL_SYNC_TOKEN"
```

### Read all rows from one table (single request)

```http
GET /tables/screen
Authorization: Bearer <MANUAL_SYNC_TOKEN>
```

Returns every row in the selected public base table in one response, with `total` and `rows`. Only actual tables in the `public` schema are readable; identifiers are looked up in Postgres metadata and quoted before use.

The current production database has one base table: `public.screen`. The API lists tables dynamically, so additional public tables will show up without a code change. Screen rows include the `lastPlayerCommsMillis` column at the top level, alongside `data`; it is sourced from Target-R `data.lastPlayerCommsMillis` and is stored as text (typically an epoch-millisecond value). When Target-R has no value, this column is `null`.

```bash
curl "$FUNCTION_URL/tables/screen" \\
  -H "Authorization: Bearer $MANUAL_SYNC_TOKEN"
```

This is one request for the full table. Very large tables can consume more memory and produce large HTTP responses; the current `screen` table has about 4,299 rows.

## Daily schedule

Trigger `targetr-screen-sync-midnight-th` invokes `POST /scheduled` with cron `0 17 * * *` (UTC), which is midnight in Thailand (UTC+7). The trigger handler verifies the Neon trigger header and that the payload identifies a schedule event. Neon schedules use UTC.

## Secrets

The Function deployment uses these environment values:

- `STACKS_USERNAME`
- `STACKS_PASSWORD`
- `MANUAL_SYNC_TOKEN`
- `URL_TARGETR` (optional; defaults to `https://stacks.targetr.net`)

Neon injects `DATABASE_URL`. Put local deployment values in `.env.local` (copy `.env.example`); it is ignored by Git. Never commit, paste, or log credentials or the manual token. If a Basic Authorization header was exposed in logs, rotate that Target-R credential.

## Deploy and manage

Install dependencies and the Neon CLI, authenticate, then link this directory to the production branch:

```bash
npm install
npm install -g neon@latest
neon login
neon link --project-id plain-voice-39403628 --branch production
```

Fill `.env.local` from `.env.example` locally, then deploy:

```bash
./scripts/deploy.sh
```

Create the daily trigger once (script is deliberately separate to avoid duplicate triggers):

```bash
./scripts/create_daily_trigger.sh
```

Useful verification commands:

```bash
neon functions get syncscreens --project-id plain-voice-39403628 --branch production
neon triggers list --project-id plain-voice-39403628 --branch production
```

The manual and table endpoints share a single bearer token. Store it in the calling service's secret manager and do not expose it in client-side/browser code. Table reads return the full selected table in one response.
