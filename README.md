# Esports Database

A PostgreSQL database for a fictional esports organization that
fields teams in Valorant, League of Legends and Rocket League. All people, sponsors, opponents and
results are made up.

## Files

| File | Purpose |
|---|---|
| `schema.sql` | Creates the 11 tables and their constraints |
| `seed.sql` | Fills the tables with data (generated, do not edit by hand) |
| `generate_data.py` | The script that generates `seed.sql` |
| `test_queries.sql` | Five test queries |
| `requirements.txt` | Python packages used by `generate_data.py` |

## Requirements

- PostgreSQL 13 or newer (tested on 17.12)
- Python 3.10 or newer (tested on 3.13), only needed to regenerate the data

## Setup on Windows (PowerShell)

**1. Install PostgreSQL** from <https://www.postgresql.org/download/windows/>. Keep the default port
(5432) and remember the password you choose for the `postgres` user. A password with only letters
and numbers is easiest, because symbols must be percent-encoded in step 4.

**2. Open PowerShell in this folder** and point to `psql`. Change `17` if you installed another
version.

```powershell
$psql = "C:\Program Files\PostgreSQL\17\bin\psql.exe"
```

**3. Create an empty database.** Enter your password if asked.

```powershell
& $psql -h localhost -U postgres -d postgres -c "CREATE DATABASE esports"
```

**4. Set the connection string.** Replace `YOUR_PASSWORD` with your own. This lasts until you close
the window.

```powershell
$env:DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@localhost:5432/esports"
```

**5. Create the tables, then load the data.**

```powershell
& $psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f schema.sql
& $psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -q -f seed.sql
```

"Does not exist, skipping" notices from `schema.sql` are normal.

**6. Check that it worked.** This should print 1096.

```powershell
& $psql $env:DATABASE_URL -c "SELECT COUNT(*) FROM player_match_stats"
```

## Setup on macOS or Linux

With PostgreSQL installed and running, and `psql` on your PATH:

```bash
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE esports"
export DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/esports"
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f seed.sql
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM player_match_stats"
```

If your PostgreSQL has no `postgres` user (common with Homebrew), use your own username instead.

## Run the test queries

Windows:

```powershell
& $psql $env:DATABASE_URL -P pager=off -f test_queries.sql
```

macOS or Linux:

```bash
psql "$DATABASE_URL" -P pager=off -f test_queries.sql
```

| # | Query | Rows |
|---|---|---|
| 1 | Each team's starters, their roles and contract end dates | 26 |
| 2 | Average kills, deaths and assists per player in one tournament | 12 |
| 3 | Current sponsorship value per team | 6 |
| 4 | Active contracts ending within 90 days | 8 |
| 5 | Players with a K/D above their team's overall K/D (at least 10 matches) | 11 |

Queries 3 and 4 use today's date. The data is built so their rows stay the same from Nov 22, 2026 to
Jan 10, 2027; only `days_left` in query 4 changes.

## Regenerate the data (optional)

`seed.sql` is already included. To recreate it on Windows:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python generate_data.py
```

On macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python generate_data.py
```

The random seed is fixed, so the result is the same every time. Add `--load` to the last command to
also load the data into `DATABASE_URL`.

## Good to know

- **Starting over:** run step 5 again. `schema.sql` deletes and recreates all 11 tables, and
  `seed.sql` (or `--load`) replaces every row in them. Check `DATABASE_URL` first.
- **Rocket League stats:** `kills` holds goals scored and `deaths` holds goals conceded.
- **Match scores** are NULL until a match is played.

## Troubleshooting

| Message | Fix |
|---|---|
| `connection refused` | Start PostgreSQL (on Windows, the `postgresql-x64-17` service) |
| `password authentication failed` | Check the password in `DATABASE_URL` |
| `database "esports" does not exist` | Do step 3 |
| `database "esports" already exists` | It is already created; go on to step 4 |
| `relation "..." does not exist` | Do step 5 |
| `No module named 'faker'` | Install the packages and run `generate_data.py` with the `.venv` Python |
