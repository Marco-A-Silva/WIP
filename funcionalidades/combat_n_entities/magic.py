from enum import IntFlag, auto

RUNETYPE = ["Core", "Expression", "Modifier"]

class dmgType(IntFlag):
    PHYSICAL = auto()
    MAGIC = auto()
    FIRE = auto()
    ICE = auto()
    WIND = auto()
    THUNDER = auto()
    SHADOW = auto()
    ILLUSORY = auto()
    SPACE = auto()
    HOLY = auto()

    def addElem(self, element):
        return self | element
    
    def rmElem(self, element):
        return self & ~element

class Spell:
    def __init__(self, runes):
        components = []
        dmgT = dmgType(0)
        effects = {}
        
        for rune in runes:
            components.append(rune.name)
            dmgT = dmgT.addElem(rune.dmgType)
            effects = effects | rune.effects

        self.components = components
        self.effects = effects
        self.dmgType = dmgT

class Rune:
    "Type es un RUNETYPE, dmgT es un dmgType, effects es un diccionario tipo {'targets': 1, 'aoe': False, 'multihit': 1}"
    def __init__(self, name, type: str, dmgT, effects):
        self.name = name
        self.type = type
        self.dmgType = dmgT
        self.effects = effects