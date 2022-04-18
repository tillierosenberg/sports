from re import I
from bs4 import BeautifulSoup
import requests
import sqlite3
import json
import os

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def api():
    lst1 =  []
    lst2 =  []
    #lst3 = []
    try:
        count_file = open("counter", "r")
        lines = count_file.readlines()
        if '1' in lines[-1]:
            count = 2
        elif '2' in lines[-1]:
            count = 3
        elif '3' in lines[-1]:
            count  = 4
        elif '4' in lines[-1]:
            count = 5
        url = "https://www.balldontlie.io/api/v1/stats?page=" + str(count)
        count_file.close()
    except:
        count = 1
        url = "https://www.balldontlie.io/api/v1/stats?page=" + str(count)
    f = open("counter" , 'w')
    f.write(str(count) + '\n')
    f.close()
    response = requests.get(url)
    j = json.loads(response.text)
    for i in range(len(j['data'])):
        id = j['data'][i]['id']
        assists = j['data'][i]['ast']
        points = j['data'][i]['pts']
        rebounds = j['data'][i]['reb']
        team_id = j['data'][i]['player']['team_id']
        team = j['data'][i]['team']['full_name']
        game_id = j['data'][i]['game']['id']
        if id != None and assists != None and points != None and rebounds != None:
            lst1.append((id, points, rebounds, assists, team_id, game_id))
            first_name = j['data'][i]['player']['first_name']
            last_name = j['data'][i]['player']['last_name']
            lst2.append((id, first_name + " " + last_name))

    return (lst1, lst2)


def create_tables(lst, cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Stats (player_id INTEGER PRIMARY KEY, points INTEGER, rebounds INTEGER, assists INTEGER, team_id INTEGER, game_id INTEGER)")
    """
    creates the database for the stats and puts the numbers into it. 
    """
    for item in lst[0]:
        cur.execute("INSERT OR IGNORE INTO Stats (player_id, points, rebounds, assists, team_id, game_id) VALUES (?,?,?,?,?,?)", (item[0], item[1], item[2], item[3], item[4], item[5]))
    cur.execute("CREATE TABLE IF NOT EXISTS Players (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    for item in lst[1]:
        cur.execute("INSERT OR IGNORE INTO Players (id, name) VALUES (?,?)", (item[0], item[1]))
    cur.execute("SELECT * from Players")
    print(len(cur.fetchall()))
    conn.commit()


def main():
    # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('DATABASE.db')
    create_tables(api(), cur, conn)
if __name__ == "__main__":
    main()