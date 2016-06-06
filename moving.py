import os, sqlite3, shutil, os, tempfile, string, random
from time import time,sleep
from subprocess import run

# Configuration
printer_name = "Zebra over USB"
libre_office_exec = "C:/Program Files (x86)/LibreOffice 5/program/soffice.exe"
sqlite_filename = "moving.db"
label_filename = "labeltemplate.fodt"

db = sqlite3.connect(sqlite_filename)

def create_temporary_copy(path):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, ''.join(random.choice(string.ascii_letters) for _ in range(10)))
    shutil.copy2(path, temp_path)
    return temp_path

def testDB():
    if len(db.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='box' OR name='audit' OR name='items');").fetchall()) != 3: createDB()
    

def createDB():
    db.execute('''CREATE TABLE box
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    info TEXT,
    floor INTEGER,
    loc TEXT NOT NULL);''')
    db.execute('''CREATE TABLE items
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    box INTEGER,
    FOREIGN KEY(box) REFERENCES box(id)
    );''')
    db.execute('''CREATE TABLE audit
    (statement TEXT NOT NULL,
    ts INT NOT NULL,
    row INT NOT NULL);''')
    db.execute('''CREATE TABLE inv
    (box INTEGER,
    loc INTEGER NOT NULL,
    ts INTEGER NOT NULL,
    FOREIGN KEY(box) REFERENCES box(id));''')
    db.commit()
    

def menu():
    os.system('cls')
    print("[1] Create Box")
    print("[2] Add items to box")
    print("[3] Print box label")
    print("[4] Scan to move")
    print("[5] Show/Edit Box")
    print("[6] Show/Edit Items")
    choice = input("Make a choice or Q to quit: ")
    if choice.lower() == "q": quit()
    options = {
        1 : createBox,
        2 : addItems,
        3 : printLabel,
        4 : scanMove,
        5 : showBox,
        6 : showItem,
        }
    options[int(choice)]()

    menu()

def showBox():
    pass

def showItem():
    pass

def scanMove():
    print("\n\n")
    print("--- Scan to move/inventory ---")
    print("q to quit")
    newLoc = input("New location name: ")
    if newLoc == "q": return
    sku = ""
    while str(sku).lower() != "q":
        sku = input("Scan: ")
        if sku.lower() == "q": return
        # Check if boxid is correct
        if sku[0:3].upper() != "BOX": continue
        if len(sku) != 6: continue
        try:
            sku = int(sku[3:])
        except ValueError:
            print("Entered scan is not BOX###")
            sleep(1)
            continue
        box = db.execute("SELECT info,floor,loc FROM box WHERE id = ?;",str(sku)).fetchone()
        bloc = getBoxInvLoc(sku)
        if bloc == None: bloc = "N/A"
        # Now save new inv line
        ts = int(time())
        db.execute("INSERT INTO inv VALUES(?,?,?);",(sku,newLoc,ts))
        db.commit()
        print("BOX{} Moved - {}->{}".format(str(sku).zfill(3),bloc[0],newLoc))

def getBoxInvLoc(boxid):
    return db.execute("SELECT loc,ts FROM inv WHERE box = ? ORDER BY ts DESC LIMIT 1;",str(boxid)).fetchone()

def createBox():
    print("\n\n")
    print("--- Create Box ---\n")
    data = input("Info about box: ")
    floor = input("What floor: ")
    loc = input("Location to put box in new place: ")
    ret = db.execute("INSERT INTO box(info,floor,loc) VALUES(?,?,?);",(data,floor,loc));
    boxid = db.execute("SELECT id FROM box WHERE ROWID = ?;",(str(ret.lastrowid))).fetchone()[0]
    db.execute("INSERT INTO audit VALUES(?,?,?);",(str(("INSERT INTO box(info,floor,loc) VALUES(?,?,?);",data,floor,loc)),int(time()),ret.lastrowid))
    print("Box {} created".format(boxid))
    db.commit()
    sleep(2)

def addItems():
    print("\n\n")
    print("--- Add items to box ---\n\nEnter \"q\" to quit.\n")
    box = input("Box: ")
    if box[0:3].upper() == "BOX":
        box = box[3:]
    try:
        box = int(box)
    except ValueError:
        print("Value for box can not be converted to an int. {}".format(box))
        addItems()
        return
    item = ""
    while item.lower() != "q":
        item = input("Item Description: ")
        if item.lower() == "q": break
        ret = db.execute("INSERT INTO items(description,box) VALUES(?,?);",(item,box))
        db.execute("INSERT INTO audit VALUES(?,?,?);",(str(("INSERT INTO items(description,box) VALUES(?,?);",item,box)),int(time()),ret.lastrowid))
        db.commit()

def printLabel():
    print("\n\n")
    print("--- Print Box Label ---\n")
    box = input("Box: ")
    if box.lower() == "q": return
    if box[0:3].upper() == "BOX" and len(box) > 3: box = box[3:]
    try:
        box = int(box)
    except ValueError:
        print("Value for box can not be converted into an int. {}".format(box))
        printLabel()
        return
    # Should have a valid int now, let's see if we can find the box row
    row = db.execute("SELECT id,info,floor,loc FROM box WHERE id = ? LIMIT 1;",(str(box))).fetchone()
    if row == None:
        print("Invalid box number. Try again. ")
        sleep(1)
        printLabel()
        return
    # Now have a box number in row[0], description in row[1], and location in row[2].
    boxid = row[0]
    boxdesc = row[1]
    boxfloor = row[2]
    boxloc = row[3]
    # Need to copy template, replace values, and print the form using run()
    #https://docs.python.org/3.5/library/subprocess.html#subprocess.run
    # Really should verify the file is here, but oh well for now
    # TODO - Uses "<text:line-break/>" for linebreaks
    template = create_temporary_copy(label_filename)
    # Build list of contents
    rows = db.execute("SELECT * FROM items WHERE box = ?;",str(box)).fetchall()
    # Should have a if len(rows) < 1, but let's leave it for now
    contents = ""
    for i in rows:
        contents += i[1] + "<text:line-break/>"
    with open(template,"r+") as f:
        fcon = f.read()
        fcon = fcon.replace("((BOX))","BOX" + str(boxid).zfill(3))
#        fcon = re.sub(r_boxid,"BOX" + str(boxid).zfill(3),fcon)
        fcon = fcon.replace("((FLOOR))",str(boxfloor))
#        fcon = re.sub(r_floor,"Floor " + str(boxfloor),fcon)
        fcon = fcon.replace("((LOC))",boxloc)
#        fcon = re.sub(r_loc,str(boxloc),fcon)
        fcon = fcon.replace("((CONTENTS))",contents)
        f.seek(0)
        f.write(fcon)
        f.truncate()
        f.close()
    # Now run LibreOffice to print
    proc = run([libre_office_exec,"--headless","-pt",printer_name,template])
    print(proc)
    print(template)
    os.remove(template)
    
    


testDB()
menu()
