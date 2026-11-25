"""
# CSC 4402 Project: Esports Organization Database
coach.py
 A menu designed for a coach of any team, the user can view roster info and are able to swap starters for substitutes. 
 They can also view the teams supporting staff, matches, player info and player totals.
"""
import db

connection = db.conn


def showRoster():
    tid = db.get_int("team id: ")
    cur = connection.cursor()
    try:
        cur.execute(
            "select p.person_id, p.gamer_tag, p.in_game_role, p.is_starter, c.end_date "
            "from player p "
            "left join player_contract c on c.player_id = p.person_id and c.status = 'Active' "
            "where p.team_id = %s order by p.is_starter desc, p.gamer_tag",
            (tid,),
        )
        rows = cur.fetchall()
    except Exception as ex:

        connection.rollback()
        print("  query error:", ex)
        cur.close()
        return

    if len(rows) == 0:
        print("  no players on team", tid, "(teams are 1 to 6)")
    else:
        print("id | tag | role | starter? | contract ends")
        for row in rows:
            print("  ", row[0], "|", row[1], "|", row[2], "|", row[3], "|", row[4])
    cur.close()


def showStaff():
    tid = db.get_int("team id: ")
    cur = connection.cursor()
    try:
        cur.execute(
            "select pe.first_name, pe.last_name, s.staff_role "
            "from staff s join person pe on pe.person_id = s.person_id "
            "where s.team_id = %s",
            (tid,),
        )
        rows = cur.fetchall()
    except Exception as ex:
        connection.rollback()
        print("  query error:", ex)
        cur.close()
        return

    if len(rows) == 0:
        print("  no staff on team", tid)
    else:
        for row in rows:
            print("  ", row)
    cur.close()


def showRecent():
    tid = db.get_int("team id: ")
    cur = connection.cursor()
    try:
        cur.execute(
            "select match_date, opponent_name, team_score, opponent_score "
            "from match where team_id = %s and team_score is not null "
            "order by match_date desc limit 10",
            (tid,),
        )
        rows = cur.fetchall()
    except Exception as ex:
        connection.rollback()
        print("  query error:", ex)
        cur.close()
        return

    if len(rows) == 0:
        print("  no played matches for team", tid)
    else:
        print("last 10 results:")
        for row in rows:
            if row[2] > row[3]:
                result = "W"
            elif row[2] < row[3]:
                result = "L"
            else:
                result = "?"
            print("  ", row[0], "vs", row[1], "score", row[2], "-", row[3], result)
    cur.close()


def showTop():
    tid = db.get_int("team id: ")
    cur = connection.cursor()
    try:
        cur.execute(
            "select player_id, count(*), sum(kills), sum(deaths), sum(assists) "
            "from player_match_stats s "
            "join player p on p.person_id = s.player_id "
            "where p.team_id = %s group by player_id",
            (tid,),
        )
        rows = cur.fetchall()
    except Exception as ex:
        connection.rollback()
        print("  query error:", ex)
        cur.close()
        return

    if len(rows) == 0:
        print("  no stats for team", tid)
    else:
        print("player id | matches | kills | deaths | assists")
        for row in rows:
            print("  ", row)
    cur.close()


def toggleStarter():
    pid = db.get_int("player id: ")
    cur = connection.cursor()
    try:
        cur.execute("update player set is_starter = not is_starter where person_id = %s returning is_starter", (pid,))
        row = cur.fetchone()
        connection.commit()
    except Exception as ex:
        connection.rollback()
        print("  update error:", ex)
        cur.close()
        return

    if row is None:
        print("  no player with that id")
    else:
        print("  is_starter is now", row[0])
    cur.close()


def start():
    while True:
        pick = db.menu("coach", {
            "1": "my roster",
            "2": "team staff",
            "3": "recent results",
            "4": "player totals",
            "5": "swap starter / sub",
            "0": "back",
        })

        if pick == "0":
            break

       
        try:
            if pick == "1":
                showRoster()
            elif pick == "2":
                showStaff()
            elif pick == "3":
                showRecent()
            elif pick == "4":
                showTop()
            elif pick == "5":
                toggleStarter()
            else:
                print("try again")
        except Exception as ex:
            connection.rollback()
            print("  something went wrong:", ex)


if __name__ == "__main__":
    start()