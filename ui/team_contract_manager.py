"""
 CSC 4402 Project: Esports Organization Database
 team_contract_manager.py
  A menu designed for a contract manager, the menu allows users to list
    all teams in the organization, view the full contract history for players,
      add new contracts or update/delete existing contracts as well as move players across
        teams without altering the players record
"""
import db

connection = db.conn


def showTeams():
    cur = connection.cursor()
    cur.execute("select team_id, team_name from team order by team_id")
    print("team id | team name")
    for row in cur.fetchall():
        print("   ", row[0], "   ", row[1])
    cur.close()


def showContracts():
    pid = input("player id (leave blank for all): ").strip()
    cur = connection.cursor()
    if pid == "":
        cur.execute("select contract_id, player_id, start_date, end_date, annual_salary, status from player_contract")
    else:
        try:
            pid = int(pid)
        except ValueError:
            print("player id has to be a number")
            cur.close()
            return
        cur.execute("select contract_id, player_id, start_date, end_date, annual_salary, status from player_contract where player_id = %s", (pid,))
    db.show_rows(cur)
    cur.close()


def addContract():
    pid = db.get_int("player id: ")
    start = input("start date (yyyy-mm-dd): ").strip()
    end = input("end date (yyyy-mm-dd): ").strip()
    salary = input("salary: ").strip()

    try:
        salary = float(salary)
    except ValueError:
        print("salary needs to be a number")
        return

    cur = connection.cursor()

    # saw a note in generate_data.py that a player should only have
    # one active contract at a time, so checking that here too
    cur.execute("select count(*) from player_contract where player_id = %s and status = 'Active'", (pid,))
    howmany = cur.fetchone()[0]
    if howmany > 0:
        print("that player already has an active contract, change the old one first")
        cur.close()
        return

    try:
        cur.execute(
            "insert into player_contract (player_id, start_date, end_date, annual_salary, status) values (%s, %s, %s, %s, 'Active') returning contract_id",
            (pid, start, end, salary),
        )
        newid = cur.fetchone()[0]
        connection.commit()
        print("saved, new contract id is", newid)
    except Exception as e:
        connection.rollback()
        print("database said no:", e)
    cur.close()


def updateContract():
    cid = db.get_int("contract id: ")
    print("1 - salary")
    print("2 - end date")
    print("3 - status")
    pick = input("which one? ").strip()

    cur = connection.cursor()

    if pick == "1":
        val = input("new salary: ").strip()
        try:
            val = float(val)
        except ValueError:
            print("not a number")
            cur.close()
            return
        cur.execute("update player_contract set annual_salary = %s where contract_id = %s", (val, cid))
    elif pick == "2":
        val = input("new end date (yyyy-mm-dd): ").strip()
        cur.execute("update player_contract set end_date = %s where contract_id = %s", (val, cid))
    elif pick == "3":
        val = input("new status (Active / Expired / Terminated): ").strip()
        cur.execute("update player_contract set status = %s where contract_id = %s", (val, cid))
    else:
        print("not a real choice")
        cur.close()
        return

    connection.commit()
    print("ok, updated", cur.rowcount, "row")
    cur.close()


def deleteContract():
    cid = db.get_int("contract id to delete: ")
    sure = input("are you sure? y/n: ").strip()
    if sure != "y":
        print("ok not deleting")
        return

    cur = connection.cursor()
    cur.execute("delete from player_contract where contract_id = %s", (cid,))
    connection.commit()
    print("deleted", cur.rowcount, "row")
    cur.close()


def movePlayer():
    pid = db.get_int("player id: ")
    tid = db.get_int("new team id: ")
    cur = connection.cursor()
    cur.execute("update player set team_id = %s where person_id = %s", (tid, pid))
    connection.commit()
    print("moved", cur.rowcount, "player")
    cur.close()


def start():
    while True:
        pick = db.menu("team contract manager", {
            "1": "show teams",
            "2": "show contracts",
            "3": "add a contract",
            "4": "update a contract",
            "5": "delete a contract",
            "6": "move player to new team",
            "0": "back",
        })

        if pick == "0":
            break

        if pick == "1":
            showTeams()
        elif pick == "2":
            showContracts()
        elif pick == "3":
            addContract()
        elif pick == "4":
            updateContract()
        elif pick == "5":
            deleteContract()
        elif pick == "6":
            movePlayer()
        else:
            print("not one of the options")


if __name__ == "__main__":
    start()