import requests
import sqlite3
import json
import os
import matplotlib.pyplot as plt

def makeDB(name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+name)
    cur = conn.cursor()
    return cur, conn

def get_data(cur, conn):
    while True:
        name_L = []
        constructor_L = []
        full_L = []
        year = input("What year would you like the standings for? Type done if you are finished ")
        if year.upper() == 'DONE':
            break
        if int(year)<1950 or int(year)>2021:
            print("Sorry, that year's standings are not available. Try entering a year between 1950 and 2021.")
            continue
        if int(year)<2022 and int(year)>=1950:
            url = "http://ergast.com/api/f1/{}/driverStandings.json?limit=25"
            requests_url = url.format(int(year))
            r = requests.get(requests_url)
            loaded_data = json.loads(r.text)
            y = loaded_data['MRData']['StandingsTable']['season']
            for items in loaded_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']:
                name_L.append(items['Driver']['givenName']+" "+items['Driver']['familyName'])
                constructor_L.append(items['Constructors'][0]['name'])
                full_L.append((items['Driver']['givenName']+" "+items['Driver']['familyName'], y, items['position'], items['Constructors'][0]['name']))
        cur.execute("CREATE TABLE IF NOT EXISTS F1_Driver_Names (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
        for name in name_L:
            cur.execute("INSERT OR IGNORE INTO F1_Driver_Names (name) VALUES (?)", (name,))
        cur.execute("CREATE TABLE IF NOT EXISTS F1_Constructor_Names (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, constructor TEXT UNIQUE)")
        for constructor in constructor_L:
            cur.execute("INSERT OR IGNORE INTO F1_Constructor_Names (constructor) VALUES (?)", (constructor,))
        cur.execute("CREATE TABLE IF NOT EXISTS F1_Position_Data (id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, driver_id INTEGER, year INTEGER, finish INTEGER, constructor_id INTEGER)")
        for tups in full_L:
            cur.execute("SELECT id FROM F1_Driver_Names WHERE name = ?", (tups[0],))
            driver_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM F1_Constructor_Names WHERE constructor = ?", (tups[3],))
            constructor_id = cur.fetchone()[0]
            cur.execute("INSERT OR IGNORE INTO F1_Position_Data (driver_id, year, finish, constructor_id) VALUES (?, ?, ?, ?)", (driver_id, tups[1], tups[2], constructor_id))
        conn.commit()
    return full_L

def calculations(cur):
    d = {}
    cur.execute("""SELECT F1_Driver_Names.name, F1_Position_Data.year, F1_Position_Data.finish, F1_Constructor_Names.constructor FROM F1_Position_Data JOIN F1_Driver_Names ON 
    F1_Driver_Names.id = F1_Position_Data.driver_id JOIN F1_Constructor_Names ON F1_Constructor_Names.id = F1_Position_Data.constructor_id""")
    for row in cur:
        if row[3] in d:
            d[row[3]].append(row[2])
        else:
            d[row[3]]=[]
            d[row[3]].append(row[2])
    for keys in d:
        avg = d[keys]
        d[keys] = sum(avg)/len(avg)
    sorted_d = sorted(d.items(), key = lambda x: x[1])
    return sorted_d

def write_file(calcs, file_name):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    with open(path + file_name,"w") as f:
        f.write("Constructor,Average Finish Over User Inputted Years\n")
        for tups in calcs:
            f.write(tups[0]+","+str(tups[1])+"\n")

def make_visualization(calcs):
    x_axis = []
    y_axis = []
    for tups in calcs[:20]:
        x_axis.append(tups[0])
        y_axis.append(tups[1])
    plt.bar(x_axis, y_axis, color = '#CCCCFF', edgecolor = 'black')
    plt.title("Average Constructor Finish In User Inputted Years (Top 20)", fontname = "Times New Roman", size = 22, fontweight = "bold")
    plt.ylabel("Average Position Finished", fontname = "Times New Roman", size = 12, fontweight = 'bold')
    plt.xlabel("Constructor", fontname = "Times New Roman", size = 12, fontweight = 'bold')
    plt.tick_params(axis='x', which='major', labelsize=6)
    plt.show()

def main():
    cur, conn = makeDB("DATABASE.db")
    get_data(cur, conn)
    write_file(calculations(cur), "f1file.csv")
    make_visualization(calculations(cur))

main()