from re import I
from bs4 import BeautifulSoup
import requests
import sqlite3
import json
import os

def setUpDatabase(db_name):
    ''' takes in a string that will name the database and then sets up data base'''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn
def response():
    '''gets response from the request from the website and parses through the website to get information about each player  '''
    resp=requests.get('https://firstsportz.com/top-100-highest-paid-athletes-conor-mcgregor/')
    soup = BeautifulSoup(resp.content, 'html.parser')
    players = soup.find_all('tr' )
    return players
def bs2():
    '''parses through the players and extracts specific data (rank, name, team, salary, endorsments, total earnings)'''
    players = response()
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
        salary = lst[3]
        endorsments = lst[4]
        earnings= float(lst[5][1:-1])
        # print((rank,name))
        if 'K' in salary:
            salary = float(salary[1:-1]) * 1000
        elif 'M' in salary:
            salary = float(salary[1:-1]) * 1000000
        if 'K' in endorsments:
            endorsments = float(endorsments[1:-1]) * 1000
        elif 'M' in endorsments:
            endorsments = float(endorsments[1:-1]) * 1000000
        lst_of_tup.append((rank,name, team, salary, endorsments, earnings*1000000))
    # print(lst_of_tup)     
    return lst_of_tup       
   
    
def table0(cur,conn):
    '''creates table for teams that includes the team name and creates an ID for that team'''
    players = response()
    lst_of_tup=[]
    for player in players[1:]:
        player.find_all('td')
        lst=[]
        for item in player:
            lst.append(item.text)
        team = lst[2]
        lst_of_tup.append(team)
    cur.execute("CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, team TEXT UNIQUE)")
    for team in lst_of_tup:

        cur.execute("INSERT OR IGNORE INTO Teams (team) VALUES (?)", (team,))
    conn.commit()
def table(cur, conn, lst_of_tup):
    """
    takes in a list of tuples that contain information about each player 
    and creates a table of players that includes all of the information that we extracted
    """
    cur.execute("CREATE TABLE IF NOT EXISTS Earnings (id INTEGER UNIQUE PRIMARY KEY, rank INTEGER, name TEXT, team INTEGER, salary INTEGER, endorsments INTEGER, earnings INTEGER)")
    cur.execute('SELECT COUNT(name) FROM Earnings')
    start = cur.fetchone()[0]
    count = 0+start
#     #need to limit this to 25 per time
    for num in range(start,start+25):
        cur.execute('SELECT id FROM Teams WHERE team = ?',(lst_of_tup[num][2],))
        team_id = cur.fetchone()[0]
        # print(type(team_id))
        cur.execute("INSERT OR IGNORE INTO Earnings (id, rank, name, team, salary, endorsments, earnings) VALUES (?, ?, ?, ?, ?, ?, ?)", (count, lst_of_tup[num][0],lst_of_tup[num][1],team_id,lst_of_tup[num][3], lst_of_tup[num][4], lst_of_tup[num][5]))
        count=count+1
    conn.commit()
def main():
    '''sets up the code in the correct order to run it'''
    cur, conn = setUpDatabase('DATABASE.db')
    table0(cur,conn)
    table(cur,conn,bs2())

if __name__ == "__main__":
    main()