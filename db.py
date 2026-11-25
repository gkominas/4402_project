"""
# CSC 4402 Project: Esports Organization Database
db.py 
shared stuff for the menu programs
"""
# db.py - shared stuff for the menu programs
# we all use the same connection settings from the README
# (the DATABASE_URL thing)

import os
import sys
import psycopg

url = os.environ.get("DATABASE_URL")

if url is None:
    print("you forgot to set DATABASE_URL")
    sys.exit()

# open one connection and reuse it. tried opening a new one for
# every menu option but then kept forgetting to commit so nothing saved
conn = psycopg.connect(url)


def show_rows(cursor):
    # print the query result as plain rows
    rows = cursor.fetchall()
    if len(rows) == 0:
        print("  nothing found")
        return
    for row in rows:
        print("  ", row)


def menu(title, choices):
    print("")
    print("-----", title, "-----")
    for k in choices:
        print(" ", k + ".", choices[k])
    answer = input("pick one: ")
    return answer.strip()


def get_int(text):
    # had a crash when i typed a letter instead of a number,
    # so now this keeps asking
    while True:
        x = input(text).strip()
        try:
            return int(x)
        except ValueError:
            print("  that was not a number, try again")