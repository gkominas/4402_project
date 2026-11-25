"""
 CSC 4402 Project: Esports Organization Database
 sponsorship_manager.py
 A menu designed for a sponsorship manager, the menu allows users to list sponsorship deal info,
   annual sponsorship value per team, and sponsor info. Users can also
     create, update, or delete sponsors and sponsorship deals.
 """

import db

connection = db.conn


def showSponsors():
    cur = connection.cursor()
    cur.execute("select sponsor_id, name, industry from sponsor order by sponsor_id")
    for row in cur.fetchall():
        print("  ", row[0], "-", row[1], "(", row[2], ")")
    cur.close()


def showValue():
    cur = connection.cursor()
    # copied the "today between start and end" trick from the test queries file
    cur.execute(
        "select t.team_name, count(*), sum(s.annual_value) from sponsorship s "
        "join team t on t.team_id = s.team_id "
        "where current_date between s.start_date and s.end_date "
        "group by t.team_name order by sum(s.annual_value) desc"
    )
    print("team | deals | total")
    for row in cur.fetchall():
        print("  ", row[0], "|", row[1], "|", row[2])
    cur.close()


def showDeals():
    raw = input("team id (blank for all): ").strip()
    cur = connection.cursor()
    sql = (
        "select s.sponsorship_id, sp.name, t.team_name, s.annual_value, "
        "s.start_date, s.end_date from sponsorship s "
        "join sponsor sp on sp.sponsor_id = s.sponsor_id "
        "join team t on t.team_id = s.team_id"
    )
    if raw == "":
        cur.execute(sql + " order by s.sponsorship_id")
    else:
        try:
            tid = int(raw)
        except ValueError:
            print("team id has to be a number")
            cur.close()
            return
        cur.execute(sql + " where s.team_id = %s order by s.start_date", (tid,))

    for row in cur.fetchall():
        print("  ", row)
    cur.close()


def addSponsor():
    n = input("sponsor name: ").strip()
    i = input("industry: ").strip()
    e = input("contact email (can leave blank): ").strip()

    if e == "":
        e = None

    cur = connection.cursor()
    try:
        cur.execute("insert into sponsor (name, industry, contact_email) values (%s, %s, %s) returning sponsor_id", (n, i, e))
        newid = cur.fetchone()[0]
        connection.commit()
        print("added sponsor, id is", newid)
    except Exception as ex:
        connection.rollback()
        print("could not add:", ex)
    cur.close()


def addDeal():
    sid = db.get_int("sponsor id: ")
    tid = db.get_int("team id: ")
    v = db.get_int("annual value: ")
    s = input("start date: ").strip()
    e = input("end date: ").strip()

    cur = connection.cursor()
    try:
        cur.execute(
            "insert into sponsorship (sponsor_id, team_id, annual_value, start_date, end_date) values (%s, %s, %s, %s, %s) returning sponsorship_id",
            (sid, tid, v, s, e),
        )
        newid = cur.fetchone()[0]
        connection.commit()
        print("new deal id:", newid)
    except Exception as ex:
        connection.rollback()
        print("error:", ex)
    cur.close()


def updateDeal():
    spid = db.get_int("sponsorship id: ")
    v = db.get_int("new value: ")
    e = input("new end date: ").strip()
    cur = connection.cursor()
    cur.execute("update sponsorship set annual_value = %s, end_date = %s where sponsorship_id = %s", (v, e, spid))
    connection.commit()
    print("updated", cur.rowcount, "row")
    cur.close()


def deleteDeal():
    spid = db.get_int("sponsorship id to delete: ")
    yes = input("delete it? y/n: ").strip()
    if yes != "y":
        print("ok nothing deleted")
        return
    cur = connection.cursor()
    cur.execute("delete from sponsorship where sponsorship_id = %s", (spid,))
    connection.commit()
    print("deleted", cur.rowcount, "row")
    cur.close()


def start():
    while True:
        pick = db.menu("sponsorship manager", {
            "1": "show sponsors",
            "2": "current value per team",
            "3": "show deals",
            "4": "add a sponsor",
            "5": "add a deal",
            "6": "update a deal",
            "7": "delete a deal",
            "0": "back",
        })

        if pick == "0":
            break

        if pick == "1":
            showSponsors()
        elif pick == "2":
            showValue()
        elif pick == "3":
            showDeals()
        elif pick == "4":
            addSponsor()
        elif pick == "5":
            addDeal()
        elif pick == "6":
            updateDeal()
        elif pick == "7":
            deleteDeal()
        else:
            print("that was not a choice")


if __name__ == "__main__":
    start()