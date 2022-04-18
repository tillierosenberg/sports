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
def bs2():
    resp=requests.get('https://firstsportz.com/top-100-highest-paid-athletes-conor-mcgregor/')
    soup = BeautifulSoup(resp.content, 'html.parser')
    players = soup.find_all('tr' )
    lst_of_tup=[]
    for player in players[1:]:
        player.find_all('td')
        lst=[]
        for item in player:
            lst.append(item.text)
        # print(lst)
        rank = lst[0]
        name = lst[1]
        team = lst[2]
        earnings=float(lst[5][1:-1])
        # print((rank,name))
        lst_of_tup.append((rank,name, team, earnings))
    # print(lst_of_tup)     
    return lst_of_tup       
   
    
def table0(cur,conn):
    resp=requests.get('https://firstsportz.com/top-100-highest-paid-athletes-conor-mcgregor/')
    soup = BeautifulSoup(resp.content, 'html.parser')
    players = soup.find_all('tr' )
    lst_of_tup=[]
    for player in players[1:]:
        player.find_all('td')
        lst=[]
        for item in player:
            lst.append(item.text)
        # print(lst)
        team = lst[2]
        # print((rank,name))
        lst_of_tup.append(team)
    # print(lst_of_tup)     
    
    cur.execute("CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, team TEXT UNIQUE)")
    for team in lst_of_tup:

        cur.execute("INSERT OR IGNORE INTO Teams (team) VALUES (?)", (team,))
    conn.commit()
def table(cur, conn, lst_of_tup):
    """
    creates the database for the menu and puts the foods into it. 
    """
    cur.execute("CREATE TABLE IF NOT EXISTS Earnings (id INTEGER UNIQUE PRIMARY KEY, rank INTEGER, name TEXT , team INTEGER, earnings TEXT)")
    cur.execute('SELECT COUNT(name) FROM Earnings')
    start = cur.fetchone()[0]
    count = 0+start
#     #need to limit this to 25 per time
    for num in range(start,start+25):
        cur.execute('SELECT id FROM Teams WHERE team = ?',(lst_of_tup[num][2],))
        team_id = cur.fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO Earnings (id, rank, name, team, earnings) VALUES (?, ?, ?, ?, ?)", (count, lst_of_tup[num][0],lst_of_tup[num][1],team_id,lst_of_tup[num][3]))
        count=count+1
    conn.commit()
def main():
#     # SETUP DATABASE AND TABLE
    cur, conn = setUpDatabase('DATABASE.db')
    table0(cur,conn)
    table(cur,conn,bs2())

if __name__ == "__main__":
    main()