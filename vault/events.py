from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs
from funcionalidades.combat_n_entities.combat_items import Item
from vault.items import shopItems
import pygame, random

class Event:
    def __init__(self,description,stat,choice,actions,rewards,consequences,odds, answer:int = 0, roll:int = 0):
        self.description = description
        self.stat = stat
        self.choice = choice
        self.actions = actions
        self.rewards = rewards
        self.consequences = consequences
        self.odds = odds
    
    def resolveEvent(self, context):
        if self.roll >= self.odds + 7:
            action = self.rewards[self.answer][0]  # Critical Success
        elif self.roll >= self.odds:
            action = self.rewards[self.answer][1]  # Success
        elif self.roll <= self.odds - 7:
            action = self.consequences[self.answer][1] # Critical Failure
        else:
            action = self.consequences[self.answer][0]  # Failure

        print(self.roll)
        context["addNotification"](action[1],2.5)
        action[0](context)

class staticEvent:
    def __init__(self,description,choice,actions,options, conditions: list = [lambda context: True for i in range(3)], consequences: list = []):
        self.description = description
        self.choice = choice
        self.actions = actions
        self.options = options
        self.conditions = conditions
        self.consequences = consequences
        self.answer = -1
    
    def resolveEvent(self,context):

        condMet = self.conditions[self.answer](context)
        action = self.options[self.answer] if condMet else self.consequences[self.answer] 

        context["addNotification"](action[1],1)
        action[0](context)
        
        
"Vitality(0)/Mind(1)/Inteligence(2)/Strength(3)/Luck(4)/Charisma(5)/Awareness(6)/Greed(7)"

staticEvents = [
    staticEvent("You come across a caravan of merchants, they carry all kinds of goods but most importantly food",
        "What do you do?",
        ["Follow them", "Rob them", "Disregard them"],
        [
            [
                lambda context: context["addRoom"]("shop"),
                "You follow the merchants until they make it to a camping spot"
            ],
            [
                lambda context: (context["player"].equip_armament(Item()),modifyAttrs(context["player"],{"gd": lambda x: x+200}),context["removeRoom"]("shop",10)),
                "You manage to rob the merchants, as a retaliation, they have escpaed to the next floor, no shops for you"
            ],
            [
                lambda context: None,
                "You continue your way"
            ]
        ],
        conditions=[lambda context: context["player"].statBlock[7] >= 6,lambda context: context["player"].statBlock[6] < 5, lambda context: True],
        consequences=[

        ]
    ),
    staticEvent(
        "A wandering healer approaches you offering aid in exchange for some money (25g)",
        "Do you accept the healer’s offer?",
        ["Accept", "Refuse"],
        [
            [
                lambda context: modifyAttrs(context["player"],{"hp": lambda x: x + context["player"].max_hp*0.15,"gd": lambda x: x-25}),
                "You accept the healer's offer, healing you (15% max hp) and costing you a pretty peny(25g)" 
            ],
            [
                lambda context: None,
                "You continue your way",
            ],
        ],
        conditions = [lambda context: context["player"].gd > 40, lambda context: True],
        consequences=[
            [
                lambda context: context["player"].modifyAttrs(context["player"],{"hp": lambda x: x - context["player"].max_hp*0.15, "gd": 0, "gre": 2}),
                "You tried to scam the healer because you had no gold, you instead got cursed with decay (-15% max hp), she takes all your money anyways",
               
            ],
            [
                lambda context: None,
                "You continue your way"
            ],
        ]
    ),
    staticEvent(
        "A hidden spring glows under the moonlight, radiating gentle warmth.",
        "Do you bathe in the waters?",
        ["Enter the spring", "Collect water"],
        [
            [
                lambda context: None,
                "You enter the spring, bathing in its allmighty waters and feeling as your mind and body were born anew ()"
            ],
            [
                lambda context: None,
                "You've collected water from said spring (gained a bottle of spring water) and you procede to leave"
            ]
        ],
    ),
    staticEvent(
        "You come across an abandoned library, and there is a book that's caught your attention, what do you do?",
        "Investigate Book?",
        ["Open it", "Inspect it"],
        [
            [
                lambda context: None,
                "You sit on the table closest to you, and as you looked at the book the pages of the kept flipping, feeding your mind with its ancient knowledge ()"
            ],
            [
                lambda context: None,
                "The book looks majestic, its cover immaculate, and you cant help but admire it, altough you are scared of the possibilities that opening it can bring and so you leave it on a table near you ()"
            ],
        ]
    ),
    staticEvent(
        "You stumble upon a recently abandoned campsite. The embers are still warm.",
        "Do you look around?",
        ["Rest", "Check the Perimeter"],
        [
            [
                lambda context: context["addRoom"]("extra_rest site"),
                "The cozy vibes of the campsite lulled you to a long and comfy rest ()"
            ],
            [
                lambda context: None,
                "As you check the surrounding rooms, you find what seems to be remnants of a hurried exit and a bunch of coins ()"
            ]
        ]
    ),
    staticEvent("A man offers you an armament for your adventure, he says 'Here, its dangerous to go alone'",
        "Accept the offer?",
        ["Yes", "Rather not"],
        [
            [
                lambda context: None,
                "'Here, you may have this item that has been bestowed upon me by the Ascended' ()"
            ],
            [
                lambda context: None,
                "'No worries brave one, at least let an old man give you some nourishment for your adventure' ()"
            ],
        ]
    ),
    staticEvent("A man offers you an armament for your adventure, he says 'Here, you wouldnt want to go alone'",
        "Accept the odd offer?",
        ["Yes", "Rather not"],
        [
            [
                lambda context: None,
                "'Here, you may have this item that has been bestowed upon me by the Cursed' ()"
            ],
            [
                lambda context: None,
                "'Fine then, you shall take your leave' ()"
            ],
        ]
    ),
    staticEvent(
        "A shimmering spirit appears on the path, offering to share wisdom.",
        "Do you seek its guidance?",
        ["Accept guidance", "Ask for a parting blessing"],
        [
            [
                lambda context: None,
                "The spirit grows and envelops you, eventually becoming a part of you, thus being able to guide you till death do you apart ()"
            ],
            [
                lambda context: None,
                "The spirit decides to give you a small fey light that will help you if you ever come across a dark place or corrupt foes ()"
            ]
        ]
    ),
    staticEvent(
        "A small abandoned shrine sits by the path, covered in moss and sludge.",
        "Do you examine it?",
        ["Search Offering Box", "Clean the Shrine"],
        [
            [
                lambda context: None,
                "You continue your way"
            ],
            [
                lambda context: None,
                "You continue your way"
            ]
        ],
    ),
    staticEvent(
        "You find a hidden entrance that leads to a room with ominous aura, but you can see a shining object in the back of it",
        "Do you risk combat for riches?",
        ["Risk it","Rather not"],
        [
            [
                lambda context: context["addRoom"]("elite"),
                "You tense your muscles in readiness to fight, for a dangerous surprise is sure to catch you offguard ()"
            ],
            [
                lambda context: None,
                "You continue your path as intended, finding it odd how the room just vanished from existance as you jogged by ()"
            ]
        ],
    ),
    staticEvent(
        "You've fallen into a trap, you now find yourself at the mercy of the dungeon and its monsters",
        "Do you struggle?",
        ["Struggle", "Take the L"],
        [
            [
                lambda context: None,
                "You continue your way"
            ],
            [
                lambda context: None,
                "You continue your way"
            ]
        ],
    ),
    staticEvent(
        "A foul odor rises from a murky river of blood. As you get closer, toxic fumes overwhelm you.",
        "Do you investigate anyway?",
        ["Yes", "No"],
        [
            [
                lambda context: None,
                "Upon closer inspection, the river of blood was filled with a deadly toxin, instantly overpowering your sense of smell and making you black out, you wake up a bit dazed, and realized you had been attacked by some type of poisonous monster and later robbed of some of your belongings ()"
            ],
            [
                lambda context: None,
                "As you go over the large river of blood, you notice its trail goes to a crevice in the wall where a mounstrous poisonous frog was waiting, you succesfully escaped its trap"
            ]
        ],
    ),
    staticEvent(
        "A pack of wolves circles you silently, their glowing eyes fixed on you.",
        "Do you try to scare them away?",
        ["Fight", "Intimidate"],
        [
            [
                lambda context: None,
                "The encounter was ferocious, it was a bloodfrenzied battle for survival, outnumbered yet you rise victorious from the corpses of your enemies ()"
            ],
            [
                lambda context: None,
                "You continue your way"
            ]
        ],
    ),
    staticEvent(
        "As you were exploring a cave within the walls of the dungeon, its starts to crumble",
        "Do you try to escape?",
        ["Sprint Out", "Brace Yourself"],
        [
            [
                lambda context: None,
                "You make a run for it and barely escape, altough not without some scars",
            ],
            [
                lambda context: None,
                "You hide under a rock formation, straining all your muscles trying to keep it together, it works",
            ]
        ],
        conditions=[lambda context: context["player"].statBlock[9] >= 6,lambda context: context["player"].statBlock[0] >= 8],
        consequences=[
            [
                lambda context: None,
                "You trip on the way to the exit, after being maimed by the falling rocks, you miraculously manage to escape the death trap",
            ],
            [
                lambda context: None,
                "For some reason you just stood there and tried to tank it, clearly had no chance of survival, you do get found by some thieves who take you out of the cave just to steal from you tho",
            ]
        ]
    ),
]


combatEvents = [

]

badEvents= []
neutralEvents = []
goodEvents = []