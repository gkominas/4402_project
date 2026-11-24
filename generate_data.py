"""
CSC 4402 Project: Esports Organization Database
generate_data.py - fills all 11 tables with realistic, consistent sample data.

    pip install -r requirements.txt
    python generate_data.py            # writes seed.sql (no database needed)
    python generate_data.py --load     # also runs it against $DATABASE_URL

Run schema.sql first. Seeding REPLACES all rows in the 11 project tables.

The random seed is fixed, so everyone gets an identical seed.sql.
Dates are fixed too: no tournament, contract or sponsorship starts or ends between
WINDOW_START and WINDOW_END, so queries using CURRENT_DATE give the same
answers on any day in that range.
"""

import argparse
import os
import random
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

from faker import Faker

SEED = 4402
OUTPUT = Path(__file__).resolve().parent / "seed.sql"

WINDOW_START = date(2026, 11, 22)
WINDOW_END = date(2027, 1, 10)
ROSTER_LOCK = date(2026, 1, 10)      # every player is signed by this date
SUBS_PER_TEAM = 2
SUB_PLAYS_CHANCE = 0.15              # chance that one starter is rested

rng = random.Random(SEED)
fake = Faker("en_US")
fake.seed_instance(SEED)

# ---------------------------------------------------------------------
# Fixed reference data
# ---------------------------------------------------------------------
GAMES = [  # title, genre, team_size
    ("Valorant", "Tactical FPS", 5),
    ("League of Legends", "MOBA", 5),
    ("Rocket League", "Sports", 3),
]

TEAMS = [  # game_id, name, roster_type, chance of winning a match
    (1, "Bayou Bolt Valorant", "Main", 0.62),
    (1, "Bayou Bolt Valorant Academy", "Academy", 0.46),
    (2, "Bayou Bolt LoL", "Main", 0.54),
    (3, "Bayou Bolt RL", "Main", 0.66),
    (2, "Bayou Bolt LoL Academy", "Academy", 0.40),
    (3, "Bayou Bolt RL Academy", "Academy", 0.50),
]

ROLES = {  # one per starter; substitutes get a random one
    1: ["Duelist", "Initiator", "Controller", "Sentinel", "Flex"],
    2: ["Top", "Jungle", "Mid", "Bot", "Support"],
    3: ["Striker", "Playmaker", "Defender"],
}

# Average kills / deaths / assists per map for each role (series totals are
# stored). Rocket League has no kills, so it is generated from goals instead.
ROLE_KDA = {
    "Duelist": (18.5, 15.5, 4.0), "Initiator": (15.0, 15.0, 8.5),
    "Controller": (14.0, 14.5, 7.5), "Sentinel": (14.5, 13.5, 4.5),
    "Flex": (15.5, 14.5, 6.0),
    "Top": (2.8, 2.9, 4.5), "Jungle": (2.9, 2.8, 7.0), "Mid": (3.9, 2.4, 5.2),
    "Bot": (4.4, 2.3, 5.0), "Support": (0.8, 3.0, 9.0),
}
ROLE_GOAL_WEIGHT = {"Striker": 5, "Playmaker": 3, "Defender": 2}

WINS_NEEDED = {1: 2, 2: 2, 3: 3}     # best of 3, 3 and 5

TOURNAMENTS = [  # game_id, name, start, end, prize_pool, matches per team
    (2, "Rift Winter Split 2026", date(2026, 1, 19), date(2026, 3, 1), 150000, 15),
    (1, "Spike Circuit Spring 2026", date(2026, 2, 2), date(2026, 3, 15), 100000, 14),
    (3, "Octane Open Spring 2026", date(2026, 2, 16), date(2026, 3, 29), 60000, 14),
    (2, "Rift Summer Split 2026", date(2026, 5, 18), date(2026, 6, 28), 200000, 15),
    (1, "Spike Circuit Summer 2026", date(2026, 6, 1), date(2026, 7, 12), 125000, 14),
    (3, "Octane Open Summer 2026", date(2026, 6, 15), date(2026, 7, 26), 75000, 14),
    (2, "Rift Fall Championship 2026", date(2026, 9, 7), date(2026, 10, 18), 300000, 13),
    (1, "Spike Circuit Finals 2026", date(2026, 9, 21), date(2026, 11, 1), 250000, 14),
    (3, "Octane Grand Prix 2026", date(2026, 10, 5), date(2026, 11, 15), 120000, 13),
    (2, "Rift Winter Split 2027", date(2027, 1, 11), date(2027, 2, 21), 160000, 6),
    (1, "Spike Circuit Kickoff 2027", date(2027, 1, 18), date(2027, 2, 28), 110000, 6),
    (3, "Octane Open Winter 2027", date(2027, 1, 25), date(2027, 3, 7), 65000, 6),
]

OPPONENTS = {
    1: ["Crescent City Reapers", "Iron Pelicans", "Neon Vultures", "Static Wolves",
        "Delta Phantoms", "Copperhead Esports", "Midnight Union", "Glass Cannon",
        "Harbor Nine", "Red Mesa", "Null Sector Five", "Paper Tigers"],
    2: ["Gulf Coast Guardians", "Cypress Order", "Stormglass", "Ember Court",
        "Northlight Esports", "Golden Magpies", "Salt & Stone", "Ravenmoor",
        "Verdant Circle", "Ashfall Gaming", "Twin Rivers", "Moonlit Pact"],
    3: ["Turbo Gators", "Axle Grease", "Skyline Drifters", "Boost Theory",
        "Full Throttle Club", "Asphalt Kings", "Zero Gravity Eleven", "Torque City",
        "Overdrive Union", "Crossbar Crew", "Pitstop Heroes", "Nitro Parish"],
}

SPONSORS = [  # name, industry
    ("Gator Surge Energy", "Energy Drink"),
    ("Keystrike Peripherals", "Peripherals"),
    ("Pelican State Bank", "Banking"),
    ("Magnolia Wireless", "Telecom"),
    ("Cajun Crunch Snacks", "Food"),
    ("Voltframe PCs", "Computer Hardware"),
    ("Levee Chairs", "Furniture"),
    ("Red Stick Apparel", "Apparel"),
    ("Cloudbank Hosting", "Web Hosting"),
    ("Tigerline Auto", "Automotive"),
]

TAG_A = ["Swamp", "Neon", "Ghost", "Turbo", "Hex", "Static", "Frost", "Rogue", "Pixel",
         "Cinder", "Lunar", "Vapor", "Rapid", "Onyx", "Echo", "Solar", "Grim", "Zen"]
TAG_B = ["Gator", "Fox", "Byte", "Viper", "Heron", "Spark", "Drift", "Moth", "Raven",
         "Bolt", "Otter", "Jinx", "Comet", "Pike", "Wisp", "Crow", "Tide", "Lynx"]

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def random_date(first, last):
    return first + timedelta(days=rng.randint(0, (last - first).days))


def money(low, high, step=500):
    return Decimal(rng.randrange(low, high + 1, step)).quantize(Decimal("0.01"))


def count_around(mean):
    """A non-negative whole number near `mean`."""
    return max(0, round(rng.gauss(mean, mean * 0.22 + 0.4)))


def slug(text):
    return "".join(ch for ch in text.lower() if ch.isalnum())


# ---------------------------------------------------------------------
# Table builders. Each returns a list of row tuples in column order.
# ---------------------------------------------------------------------


def build_people():
    """person, player and staff rows."""
    persons, players, staff = [], [], []
    used_names, used_tags = set(), set()

    def new_person():
        while True:
            first, last = fake.first_name(), fake.last_name()
            if (first, last) not in used_names:
                break
        used_names.add((first, last))
        pid = len(persons) + 1
        persons.append((pid, first, last, f"{slug(first)}.{slug(last)}@bayoubolt.example"))
        return pid

    def new_tag():
        while True:
            tag = rng.choice(TAG_A) + rng.choice(TAG_B)
            if tag not in used_tags:
                used_tags.add(tag)
                return tag

    for team_id, (game_id, _, _, _) in enumerate(TEAMS, start=1):
        roles = ROLES[game_id]
        for role in roles:
            players.append((new_person(), new_tag(), role, team_id, True))
        for role in rng.sample(roles, SUBS_PER_TEAM):
            players.append((new_person(), new_tag(), role, team_id, False))

    for team_id, (_, _, roster_type, _) in enumerate(TEAMS, start=1):
        wanted = ["Head Coach", "Analyst", "Team Manager"]
        if roster_type == "Main":
            wanted.append("Assistant Coach")
        for role in wanted:
            staff.append((new_person(), role, team_id))
    for role in ["General Manager", "Partnerships Manager", "Partnerships Manager"]:
        staff.append((new_person(), role, None))     # org-wide

    return persons, players, staff


def build_contracts(players):
    """One Active contract per player plus back-to-back earlier ones."""
    expiring_soon = {p[0] for p in rng.sample(players, 8)}
    rows = []
    for player_id, _, _, team_id, is_starter in players:
        main = TEAMS[team_id - 1][2] == "Main"
        if main:
            salary = money(60000, 140000) if is_starter else money(36000, 58000)
        else:
            salary = money(24000, 40000) if is_starter else money(18000, 26000)

        start = random_date(date(2025, 3, 1), date(2026, 9, 30))
        if player_id in expiring_soon:
            end = random_date(date(2027, 1, 12), date(2027, 2, 18))
        else:
            end = random_date(date(2027, 4, 1), date(2028, 12, 31))
        history = [(player_id, start, end, salary, "Active")]

        # Walk backwards until the player was signed before the season began.
        extra = rng.choice([0, 0, 1])
        while start > ROSTER_LOCK or extra > 0:
            if start <= ROSTER_LOCK:
                extra -= 1
            end = start - timedelta(days=1)
            start = end - timedelta(days=rng.randint(180, 540))
            salary = (salary * Decimal(rng.randint(78, 95)) / 100).quantize(Decimal("1E2"))
            salary = salary.quantize(Decimal("0.01"))
            status = "Terminated" if rng.random() < 0.12 else "Expired"
            history.append((player_id, start, end, salary, status))
        rows.extend(reversed(history))
    return [(i, *row) for i, row in enumerate(rows, start=1)]


def build_tournaments():
    return [(i, g, name, start, end, Decimal(prize).quantize(Decimal("0.01")))
            for i, (g, name, start, end, prize, _) in enumerate(TOURNAMENTS, start=1)]


def build_matches():
    """Every team enters every tournament of its game, one match per day."""
    rows = []
    for tournament_id, (game_id, _, start, end, _, count) in enumerate(TOURNAMENTS, start=1):
        days = [start + timedelta(days=d) for d in range((end - start).days + 1)]
        for team_id, (team_game, _, _, win_chance) in enumerate(TEAMS, start=1):
            if team_game != game_id:
                continue
            pool = OPPONENTS[game_id]
            opponents = (rng.sample(pool, len(pool)) + rng.sample(pool, len(pool)))[:count]
            for day, opponent in zip(sorted(rng.sample(days, count)), opponents):
                when = datetime.combine(day, time(rng.randint(15, 21), rng.choice([0, 30])))
                ours = theirs = None
                if day < WINDOW_START:
                    need = WINS_NEEDED[game_id]
                    lost = rng.choice(range(need))
                    ours, theirs = (need, lost) if rng.random() < win_chance else (lost, need)
                rows.append((tournament_id, team_id, opponent, when, ours, theirs))
    rows.sort(key=lambda r: (r[3], r[1]))
    return [(i, *row) for i, row in enumerate(rows, start=1)]


def pick_lineup(team_id, players):
    roster = [p for p in players if p[3] == team_id]
    lineup = [p for p in roster if p[4]]
    if rng.random() < SUB_PLAYS_CHANCE:
        lineup[rng.randrange(len(lineup))] = rng.choice([p for p in roster if not p[4]])
    return lineup


def rocket_league_stats(lineup, ours, theirs):
    """kills = goals scored, deaths = goals conceded (charged to the beaten
    defender), assists = assists."""
    totals = {p[0]: [0, 0, 0] for p in lineup}
    ids = list(totals)
    weights = [ROLE_GOAL_WEIGHT[p[2]] for p in lineup]
    for won in [True] * ours + [False] * theirs:
        low = rng.choice([0, 1, 1, 2, 2, 3])
        high = low + rng.choice([1, 1, 2, 2, 3])
        scored, conceded = (high, low) if won else (low, high)
        for _ in range(scored):
            scorer = rng.choices(ids, weights)[0]
            totals[scorer][0] += 1
            if rng.random() < 0.65:
                totals[rng.choice([i for i in ids if i != scorer])][2] += 1
        for _ in range(conceded):
            totals[rng.choice(ids)][1] += 1
    return totals


def build_stats(matches, players):
    skill = {p[0]: rng.uniform(0.88, 1.14) for p in players}
    rows = []
    for match_id, _, team_id, _, _, ours, theirs in matches:
        if ours is None:
            continue
        game_id = TEAMS[team_id - 1][0]
        lineup = pick_lineup(team_id, players)
        if game_id == 3:
            totals = rocket_league_stats(lineup, ours, theirs)
        else:
            maps = ours + theirs
            form = 1 + 0.15 * (ours - theirs) / WINS_NEEDED[game_id]
            totals = {}
            for p in lineup:
                k, d, a = ROLE_KDA[p[2]]
                s = skill[p[0]]
                totals[p[0]] = [count_around(k * maps * s * form),
                                count_around(d * maps / (s * form)),
                                count_around(a * maps * form)]
        rows.extend((match_id, pid, *kda) for pid, kda in totals.items())
    return rows


def build_sponsors():
    return [(i, name, industry, f"partnerships@{slug(name)}.example")
            for i, (name, industry) in enumerate(SPONSORS, start=1)]


def build_sponsorships():
    """2-4 current deals per team, some with an earlier deal they renewed."""
    rows = []
    for team_id, (_, _, roster_type, _) in enumerate(TEAMS, start=1):
        main = roster_type == "Main"
        for sponsor_id in rng.sample(range(1, len(SPONSORS) + 1), rng.randint(3, 4) if main else 2):
            value = money(40000, 180000, 2500) if main else money(8000, 35000, 1000)
            start = random_date(date(2025, 9, 1), date(2026, 9, 30))
            rows.append((sponsor_id, team_id, value, start,
                         random_date(date(2027, 2, 1), date(2028, 6, 30))))
            if rng.random() < 0.4:
                old_value = (value * Decimal(rng.randint(70, 95)) / 100).quantize(Decimal("0.01"))
                rows.append((sponsor_id, team_id, old_value,
                             start - timedelta(days=366), start - timedelta(days=1)))
    rows.sort(key=lambda r: (r[3], r[1], r[0]))
    return [(i, *row) for i, row in enumerate(rows, start=1)]


# ---------------------------------------------------------------------
# Checks for rules the schema's constraints cannot express
# ---------------------------------------------------------------------


def validate(data):
    def check(ok, message):
        if not ok:
            raise SystemExit(f"Generated data is inconsistent: {message}")

    in_window = lambda d: WINDOW_START <= d <= WINDOW_END
    team_game = {t[0]: t[1] for t in data["team"]}
    team_size = {g[0]: g[3] for g in data["game"]}
    tours = {t[0]: t for t in data["tournament"]}
    player_team = {p[0]: p[3] for p in data["player"]}
    matches = {m[0]: m for m in data["match"]}

    check(not set(player_team) & {s[0] for s in data["staff"]}, "person is player and staff")

    for team_id, game_id in team_game.items():
        starters = sum(1 for p in data["player"] if p[3] == team_id and p[4])
        check(starters == team_size[game_id], f"team {team_id} starter count")

    first_signed = {}
    for pid in player_team:
        own = sorted((c for c in data["player_contract"] if c[1] == pid), key=lambda c: c[2])
        check(sum(c[5] == "Active" for c in own) == 1, f"player {pid} active contracts")
        for a, b in zip(own, own[1:]):
            check(a[3] < b[2], f"player {pid} contracts overlap")
        for c in own:
            check((c[5] == "Active") == (c[2] < WINDOW_START and c[3] > WINDOW_END),
                  f"contract {c[0]} status disagrees with its dates")
        first_signed[pid] = own[0][2]

    for m in matches.values():
        tour = tours[m[1]]
        check(team_game[m[2]] == tour[1], f"match {m[0]} game mismatch")
        check(tour[3] <= m[4].date() <= tour[4], f"match {m[0]} outside its tournament")
        check(not in_window(m[4].date()), f"match {m[0]} inside the fixed window")
        check((m[5] is None) == (m[6] is None) == (m[4].date() > WINDOW_END),
              f"match {m[0]} score presence")
        check(m[5] is None or m[5] != m[6], f"match {m[0]} is a tie")

    lineup_size = {}
    for match_id, pid, *_ in data["player_match_stats"]:
        m = matches[match_id]
        check(player_team[pid] == m[2], f"stats for wrong team in match {match_id}")
        check(first_signed[pid] <= m[4].date(), f"player {pid} played before signing")
        lineup_size[match_id] = lineup_size.get(match_id, 0) + 1
    for m in matches.values():
        expected = 0 if m[5] is None else team_size[team_game[m[2]]]
        check(lineup_size.get(m[0], 0) == expected, f"match {m[0]} lineup size")

    for s in data["sponsorship"]:
        check(not in_window(s[4]) and not in_window(s[5]), f"sponsorship {s[0]} in window")
    active_teams = {s[2] for s in data["sponsorship"]
                    if s[4] < WINDOW_START and s[5] > WINDOW_END}
    check(active_teams == set(team_game), "team without an active sponsorship")


# ---------------------------------------------------------------------
# SQL output
# ---------------------------------------------------------------------
COLUMNS = {  # parents before children; insert order matters
    "game": "game_id title genre team_size",
    "team": "team_id game_id team_name roster_type",
    "person": "person_id first_name last_name email",
    "player": "person_id gamer_tag in_game_role team_id is_starter",
    "staff": "person_id staff_role team_id",
    "player_contract": "contract_id player_id start_date end_date annual_salary status",
    "tournament": "tournament_id game_id name start_date end_date prize_pool",
    "match": "match_id tournament_id team_id opponent_name match_date team_score opponent_score",
    "player_match_stats": "match_id player_id kills deaths assists",
    "sponsor": "sponsor_id name industry contact_email",
    "sponsorship": "sponsorship_id sponsor_id team_id annual_value start_date end_date",
}
SERIAL_TABLES = ["game", "team", "person", "player_contract", "tournament", "match",
                 "sponsor", "sponsorship"]


def literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, Decimal)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def to_sql(data):
    out = [
        "-- =====================================================================",
        "-- seed.sql - GENERATED by generate_data.py; edit that file, not this one.",
        "-- Run schema.sql first. This REPLACES all rows in the 11 project tables.",
        "-- =====================================================================",
        "BEGIN;",
        "",
        f"TRUNCATE {', '.join(COLUMNS)} RESTART IDENTITY;",
    ]
    for table, columns in COLUMNS.items():
        names = columns.split()
        values = ",\n  ".join("(" + ", ".join(map(literal, row)) + ")" for row in data[table])
        out += ["", f"INSERT INTO {table} ({', '.join(names)}) VALUES\n  {values};"]
    out += ["", "-- Continue auto-numbering after the ids inserted above"]
    for table in SERIAL_TABLES:
        key = COLUMNS[table].split()[0]
        out.append(f"SELECT setval(pg_get_serial_sequence('{table}', '{key}'), "
                   f"(SELECT MAX({key}) FROM {table}));")
    return "\n".join(out + ["", "COMMIT;", ""])


def build_all():
    persons, players, staff = build_people()
    matches = build_matches()
    return {
        "game": [(i, *g) for i, g in enumerate(GAMES, start=1)],
        "team": [(i, *t[:3]) for i, t in enumerate(TEAMS, start=1)],
        "person": persons,
        "player": players,
        "staff": staff,
        "player_contract": build_contracts(players),
        "tournament": build_tournaments(),
        "match": matches,
        "player_match_stats": build_stats(matches, players),
        "sponsor": build_sponsors(),
        "sponsorship": build_sponsorships(),
    }


def load(sql):
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("--load needs the DATABASE_URL environment variable.")
    import psycopg
    # autocommit: seed.sql has its own BEGIN/COMMIT
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(sql)
        print(f"Loaded into {conn.info.dbname} on {conn.info.host}.")


def main():
    parser = argparse.ArgumentParser(description="Generate seed.sql for the esports database.")
    parser.add_argument("--load", action="store_true",
                        help="also run the SQL against $DATABASE_URL (replaces existing rows)")
    args = parser.parse_args()

    data = build_all()
    validate(data)
    sql = to_sql(data)
    OUTPUT.write_text(sql, encoding="utf-8", newline="\n")
    for table in COLUMNS:
        print(f"{table:20} {len(data[table]):6}")
    print(f"Wrote {OUTPUT}")
    if args.load:
        load(sql)


if __name__ == "__main__":
    main()
