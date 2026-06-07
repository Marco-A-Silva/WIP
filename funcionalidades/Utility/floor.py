import random

MAIN_ROOMS = ["fight","chest","shop","event","extra"]
MAIN_ODDS = [55,12,6,22,5]
EXTRA_ROOMS = ["dojo","rest site","school of magic"]
EXTRA_ODDS = [1,3,1]

ROOMS_PER_FLOOR = 9


def initializeFloorLayout(floor):
    layout = random.choices(MAIN_ROOMS,k=ROOMS_PER_FLOOR,weights=MAIN_ODDS)

    for i,room in enumerate(layout):
        if room == "extra":
            layout[i] = "extra_" + random.choices(EXTRA_ROOMS, k=1, weights=EXTRA_ODDS)[0]

    if floor % 10 == 0:
        layout.append("elite")
    else: layout.append("shop")

    return layout

def addRoom(floorLayout , key, i):
    floorLayout.insert(i,key)

def removeRoom(floorLayout, key,i):
    amount = 0
    for i,floor in enumerate(floorLayout):
        if floor == key and amount != i:
            floorLayout[i].pop()
            amount += 1

def loadNewRoom(floor, maxRoom, room, floorLayout, transition):

    if room%maxRoom == 0 and room != 0: 
        floor += 1
        floorLayout = initializeFloorLayout(floor) 
        room = 0
    activeFloor = floorLayout[room]
        
    room += 1

    return floorLayout, floor, room, activeFloor, transition, []
 