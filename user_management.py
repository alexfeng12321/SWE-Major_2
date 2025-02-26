import sqlite3 as sql
import time
import random
from hash import *

'''
#check_password(cur.execute(f"GET password FROM users WHERE username = '{username}'"), password)
# python3 user_management.py

con = sql.connect("database_files/database.db")
cur = con.cursor()
#print(check_password(cur.execute(f"Select * FROM users WHERE username = '{"hi"}'"), password))
cur.execute(f"SELECT password from users where username = 'alex'")
storedHash = cur.fetchone()[0]
print(check_password(storedHash, 'alex'))
'''


def insertUser(username, password, DoB):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
        (username, password, DoB),
    )
    con.commit()
    con.close()


def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
    if cur.fetchone() == None:
        con.close()
        return False
    else:
        #cur.execute(f"SELECT * FROM users WHERE password = '{password}'")
        #cur.execute(f"GET password FROM users WHERE username = '{username}'")
        # Plain text log of visitor count as requested by Unsecure PWA management
        with open("visitor_log.txt", "r") as file:
            number = int(file.read().strip())
            number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))
        # Simulate response time of heavy app for testing purposes
        time.sleep(random.randint(80, 90) / 1000)
        cur.execute(f"SELECT password from users where username = '{username}'")
        storedHash = cur.fetchone()[0]
        match = check_password(storedHash, password)
        if match == False:
            con.close()
            return False
        else:
            con.close()
            return True


def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO feedback (feedback) VALUES ('{feedback}')")
    con.commit()
    con.close()


def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")
        f.write("</p>\n")
    f.close()
