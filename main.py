"""
# CSC 4402 Project: Esports Organization Database
main.py
Runs main menu, calls other menus
"""


import db
import team_contract_manager
import match_analyst
import sponsorship_manager
import admin
import coach


def start():
    while True:
        pick = db.menu("bayou bolt esports", {
            "1": "team contract manager",
            "2": "match analyst",
            "3": "sponsorship manager",
            "4": "admin",
            "5": "coach",
            "0": "exit",
        })

        if pick == "0":
            print("bye")
            break
        elif pick == "1":
            team_contract_manager.start()
        elif pick == "2":
            match_analyst.start()
        elif pick == "3":
            sponsorship_manager.start()
        elif pick == "4":
            admin.start()
        elif pick == "5":
            coach.start()
        else:
            print("that is not a menu")


if __name__ == "__main__":
    start()