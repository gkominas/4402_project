"""
 CSC 4402 Project: Esports Organization Database
match_analyst.py
 match analyst -A menu designed for an analyst who must record results and player performances
   to provide commentary or advise coaches or contract/sponsorship managers. 
   The menu allows users to view upcoming, scoreless, matches, recent matches or all matches.
 The user can also enter, update, or delete scores and player statistics for a match.
"""
import db

connection = db.conn


def showUnplayed():
    cur = connection.cursor()
    cur.execute("select match_id, team_id, opponent_name, match_date from match where team_score is null order by match_date")
    print("match id | team | opponent | when")
    for row in cur.fetchall():
        print("  ", row[0], "|", row[1], "|", row[2], "|", row[3])
    cur.close()


def showPlayed():
    cur = connection.cursor()
    cur.execute("select match_id, team_id, opponent_name, match_date, team_score, opponent_score from match where team_score is not null order by match_date desc limit 20")
    print("last 20 played matches:")
    for row in cur.fetchall():
        print("  ", row[0], "|", row[2], "|", row[4], "-", row[5])
    cur.close()


def enterScore():
    mid = db.get_int("match id: ")
    ours = db.get_int("our score: ")
    theirs = db.get_int("their score: ")

    cur = connection.cursor()
    cur.execute("update match set team_score = %s, opponent_score = %s where match_id = %s", (ours, theirs, mid))
    connection.commit()
    print("updated", cur.rowcount, "match")
    cur.close()


def enterStats():
    mid = db.get_int("match id: ")
    print("typing a blank player id will stop the loop")
    count = 0

    cur = connection.cursor()
    while True:
        raw = input("player id (blank to stop): ").strip()
        if raw == "":
            break
        try:
            pid = int(raw)
        except ValueError:
            print("skipping that, not a number")
            continue

        k = db.get_int("  kills: ")
        d = db.get_int("  deaths: ")
        a = db.get_int("  assists: ")

        # got a duplicate key error here once, so using on conflict
        # to just replace the old numbers
        try:
            cur.execute(
                "insert into player_match_stats (match_id, player_id, kills, deaths, assists) values (%s, %s, %s, %s, %s) on conflict (match_id, player_id) do update set kills = excluded.kills, deaths = excluded.deaths, assists = excluded.assists",
                (mid, pid, k, d, a),
            )
            count = count + 1
        except Exception as e:
            connection.rollback()
            print("  could not save that one:", e)
            continue

    connection.commit()
    print("saved", count, "rows")
    cur.close()


def showStats():
    mid = db.get_int("match id: ")
    cur = connection.cursor()
    cur.execute(
        "select player_id, kills, deaths, assists from player_match_stats where match_id = %s",
        (mid,),
    )
    rows = cur.fetchall()
    if len(rows) == 0:
        print("no stats for that match yet")
    else:
        for r in rows:
            print("  player", r[0], "kills", r[1], "deaths", r[2], "assists", r[3])
    cur.close()


def deleteStats():
    mid = db.get_int("match id: ")
    pid = db.get_int("player id: ")
    cur = connection.cursor()
    cur.execute("delete from player_match_stats where match_id = %s and player_id = %s", (mid, pid))
    connection.commit()
    print("deleted", cur.rowcount, "row")
    cur.close()


def start():
    while True:
        pick = db.menu("match analyst", {
            "1": "show unplayed matches",
            "2": "show last 20 played",
            "3": "enter / fix a score",
            "4": "enter stats for a match",
            "5": "show stats for a match",
            "6": "delete stats for a player",
            "0": "back",
        })

        if pick == "0":
            break

        if pick == "1":
            showUnplayed()
        elif pick == "2":
            showPlayed()
        elif pick == "3":
            enterScore()
        elif pick == "4":
            enterStats()
        elif pick == "5":
            showStats()
        elif pick == "6":
            deleteStats()
        else:
            print("pick a real number")


if __name__ == "__main__":
    start()