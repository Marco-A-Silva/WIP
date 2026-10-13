from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs, Stats
from funcionalidades.combat_n_entities.combat_items import Item
from vault.items import shopItems
import pygame, random

class Event:
    def __init__(self, description, actions, stat=None, difficulty=-1):
        self.description = description
        self.actions = actions
        self.stat = stat
        self.diff = difficulty
        

    def roll(self, member):
        if self.diff == -1:
            return 1
        stat = member.statBlock[self.stat]
        diff = max(1, self.diff)
        return 1 if random.random() < stat / (stat + diff) else 0
    

    def resolve(self, action, context):
        result = self.roll(context.get("player"))
        cons = "yes" if result == 1 else "no"
        texto, efecto = self.actions[action][cons]

        out = efecto(context)
        datos = out if isinstance(out, dict) else {}

        return texto.format(**datos)

    def scaleDiff(self, base, progress, k=0.15):
        if base == -1:
            return -1
        return max(1, round(base * (1 + k * progress)))

# NO DIFF turns of the binary result, always yes

events = [
    Event( #Trade
        "You come across a passing caravan of merchants, they carry all kinds of goods but most importantly food",
        {
            "Trade for food": {"yes": ("You get your money's worth of nourishment (-{gd})", 
                lambda c: (
                    g:= min(c["player"].gd, 20) ,
                    modifyAttrs(c["player"], {"gd": ("-", g), "hp": ("+",(c["player"].max_hp*0.25*g)/20)}), 
                    {"gd":g}
                )[2])
            },
            "Trade for goods": {"yes": ("The caravan welcomes your gold", lambda c: c["addRoom"]("shop", c["nroom"]))},
            "Keep Going": {"yes": ("You let them be and continue on your way", lambda c: None)}
        }
    ),
    Event( #Trap
        "You find yourself with an ominously empty corridor",
        {
            "Cross carefully": {
                "yes": ("You spot the raised slabs and step around them. A forgotten purse waits at the end.", lambda c: modifyAttrs(c["player"], {"gd": ("+", 25)})),
                "no":  ("A plate clicks under your foot.", 
                lambda c: (
                    d := max(0, min(int(c["player"].max_hp * 0.2), c["player"].hp - 1)),
                    modifyAttrs(c["player"], {"hp": ("-", d)}),
                    {"dmg": d}
                )[2])
            },
            "Turn back": {
                "yes": ("You decide it isn't worth the risk and turn back.", lambda c: None),
                "no":  ("You decide it isn't worth the risk and turn back.", lambda c: None)
            }
        },
        Stats.LCK, 8
    ),
    Event( #Gamble
        "A wishing well.", {
            "Throw 20g": {
                "yes": ("A fortune spills out! (+60g)", lambda c: modifyAttrs(c["player"], {"gd": ("+", 60)})),
                "no":  ("Nothing happens (-{gd}g).", lambda c: (g := min(c["player"].gd, 20), modifyAttrs(c["player"], {"gd": ("-", g)}), {"gd": g})[2] )
            },
            "Leave":     {
                "yes": ("You walk away.", lambda c: None),
                "no":  ("You walk away.", lambda c: None)
            },
        }, 
        Stats.LCK, 12
    ),
    Event( #Riddle
        "A sphinx of weathered sandstone blocks the corridor. 'Answer me true, traveler: I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?'",
        {
            "A map": {"yes": (
                "The sphinx's stone lips curl into a smile. 'Correct.' She slides aside and a pouch drops at your feet (+40).",
                lambda c: modifyAttrs(c["player"], {"gd": ("+", 40)})
            )},
            "A river": {"yes": (
                "'Wrong.' The sand turns to a rushing current and sweeps your gold away (-{gd}g).",
                lambda c: (g:= min(c["player"].gd, 30),modifyAttrs(c["player"], {"gd": ("-", g)}), {"gd": g})[2]
            )},
            "A mountain": {"yes": (
                "'Wrong.' The mountain you named answers back, and a rockslide crashes down on you dealing {dmg}.",
                lambda c: (
                    d := max(0, min(int(c["player"].max_hp * 0.25), c["player"].hp - 1)),
                    modifyAttrs(c["player"], {"hp": ("-", d)}),
                    {"dmg": d}
                )[2]
            )},
        }
    ),
    Event( #Floor
        "Behind a curtain of hanging roots, you feel a faint draft where the wall should be solid.",
        {
            "Search the wall": {
                "yes": ("Your fingers find a loose stone. The wall grinds aside, revealing a narrow passage.", lambda c: c["addRoom"]("chest", c["nroom"])),
                "no":  ("You find nothing but cold stone. Whatever the draft was, it stays hidden.", lambda c: None),
            },
            "Keep going": {
                "yes": ("You leave the wall alone and move on.", lambda c: None),
                "no":  ("You leave the wall alone and move on.", lambda c: None),
            },
        },
        Stats.LCK, 10
    ),
    Event( #Combat
        "You se a slumbering monster, and what seems to be a chest behind it",
        {
            "challenge the foe": {
                "yes": ("You shout a battle cry to let them know you are to be feared", lambda c: c["addRoom"]("fight",c["nroom"])),
                "no": ("As you approach, the monster rises, awakening some primal fear in your being",lambda c: c["addRoom"]("elite",c["nroom"]))
            },
            "Sneakily keep going": {
                "yes": ("you tippy toe out of that place asap", lambda c: None),
                "no": ("While tippy toeing you trip and fall, and that seemed to wake up the beast", lambda c: c["addRoom"]("fight",c["nroom"]))
            }
        },
        Stats.LCK, 9
    ),
    Event( #Recruit
        "You find a battered warrior, laying against a wall, he pleads for you to help him", 
        {
            "Have him join your party": {
                "yes": ()
            },
            "Give him some money (5gd)": {
                "yes": ()
            },
            "Ignore him": {
                "yes": ()
            }
        }
    )
]
