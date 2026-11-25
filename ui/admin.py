"""
# CSC 4402 Project: Esports Organization Database
admin.py
admin - A menu designed for a general manager, allowing users to create, 
update and delete team info (altering the main or academy roster), people, staff, and tournaments. 
Teams with players cannot be deleted until all players are removed, 
while deleting tournaments will delete all matches that belong to it.
"""
import db

connection = db.conn


def showTeams():
    cur = connection.cursor()
    cur.execute("select team_id, game_id, team_name, roster_type from team order by team_id")
    for row in cur.fetchall():
        print("  ", row)
    cur.close()


def addTeam():
    g = db.get_int("game id (1=valorant, 2=lol, 3=rl): ")
    n = input("team name: ").strip()
    t = input("main or academy: ").strip()

    cur = connection.cursor()
    try:
        cur.execute("insert into team (game_id, team_name, roster_type) values (%s, %s, %s) returning team_id", (g, n, t))
        newid = cur.fetchone()[0]
        connection.commit()
        print("new team id is", newid)
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def renameTeam():
    tid = db.get_int("team id: ")
    n = input("new name: ").strip()
    cur = connection.cursor()
    cur.execute("update team set team_name = %s where team_id = %s", (n, tid))
    connection.commit()
    print("changed", cur.rowcount, "team")
    cur.close()


def deleteTeam():
    tid = db.get_int("team id to delete: ")
    print("warning, will not work if players are still on this team")
    yes = input("still delete? y/n: ").strip()
    if yes != "y":
        return
    cur = connection.cursor()
    try:
        cur.execute("delete from team where team_id = %s", (tid,))
        connection.commit()
        print("deleted", cur.rowcount, "team")
    except Exception as ex:
        connection.rollback()
        print("could not delete, probably still in use:", ex)
    cur.close()


def showPeople():
    cur = connection.cursor()
    cur.execute("select person_id, first_name, last_name from person order by person_id")
    for row in cur.fetchall():
        print("  ", row)
    cur.close()


def addPerson():
    f = input("first name: ").strip()
    l = input("last name: ").strip()
    e = input("email: ").strip()

    cur = connection.cursor()
    try:
        cur.execute("insert into person (first_name, last_name, email) values (%s, %s, %s) returning person_id", (f, l, e))
        newid = cur.fetchone()[0]
        connection.commit()
        print("new person id:", newid)
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def addStaff():
    pid = db.get_int("person id: ")
    r = input("staff role (head coach / assistant coach / analyst / team manager / general manager / partnerships manager): ").strip()
    raw = input("team id (blank for org-wide): ").strip()
    if raw == "":
        tid = None
    else:
        try:
            tid = int(raw)
        except ValueError:
            print("team id has to be a number")
            return

    cur = connection.cursor()
    try:
        cur.execute("insert into staff (person_id, staff_role, team_id) values (%s, %s, %s)", (pid, r, tid))
        connection.commit()
        print("staff saved")
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def deletePerson():
    pid = db.get_int("person id to delete: ")
    print("this will also remove their player / staff / contract rows")
    yes = input("still delete? y/n: ").strip()
    if yes != "y":
        return
    cur = connection.cursor()
    try:
        cur.execute("delete from person where person_id = %s", (pid,))
        connection.commit()
        print("deleted", cur.rowcount, "person")
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def showTournaments():
    cur = connection.cursor()
    cur.execute("select tournament_id, game_id, name, start_date, end_date, prize_pool from tournament order by tournament_id")
    for row in cur.fetchall():
        print("  ", row)
    cur.close()


def addTournament():
    g = db.get_int("game id: ")
    n = input("name: ").strip()
    s = input("start date: ").strip()
    e = input("end date: ").strip()
    p = db.get_int("prize pool: ")

    cur = connection.cursor()
    try:
        cur.execute(
            "insert into tournament (game_id, name, start_date, end_date, prize_pool) values (%s, %s, %s, %s, %s) returning tournament_id",
            (g, n, s, e, p),
        )
        newid = cur.fetchone()[0]
        connection.commit()
        print("new tournament id:", newid)
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def deleteTournament():
    tid = db.get_int("tournament id to delete: ")
    print("this also deletes all matches in that tournament")
    yes = input("still delete? y/n: ").strip()
    if yes != "y":
        return
    cur = connection.cursor()
    try:
        cur.execute("delete from tournament where tournament_id = %s", (tid,))
        connection.commit()
        print("deleted", cur.rowcount, "tournament")
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def start():
    while True:
        pick = db.menu("admin (general manager)", {
            "1": "show teams",
            "2": "add team",
            "3": "rename team",
            "4": "delete team",
            "5": "show people",
            "6": "add person",
            "7": "add staff",
            "8": "delete person",
            "9": "show tournaments",
            "10": "add tournament",
            "11": "delete tournament",
            "0": "back",
        })

        if pick == "0":
            break

        if pick == "1":
            showTeams()
        elif pick == "2":
            addTeam()
        elif pick == "3":
            renameTeam()
        elif pick == "4":
            deleteTeam()
        elif pick == "5":
            showPeople()
        elif pick == "6":
            addPerson()
        elif pick == "7":
            addStaff()
        elif pick == "8":
            deletePerson()
        elif pick == "9":
            showTournaments()
        elif pick == "10":
            addTournament()
        elif pick == "11":
            deleteTournament()
        else:
            print("not a valid option")


if __name__ == "__main__":
    start()