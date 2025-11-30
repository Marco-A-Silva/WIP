from funcionalidades.combat_n_entities.combat_items import OverTimeEffects
from funcionalidades.combat_n_entities.combat_items import modifyAttrs
import pygame, time




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
        context["addNotification"](action[1])
        action[0](context)
        
        
"Vitality(0)/Mind(1)/Inteligence(2)/Strength(3)/Luck(4)/Charisma(5)/Awareness(6)/Greed(7)"


# Events that are good yet can end badly
goodEvents = [
    Event("",
        (7,),
        "",
        ["Shop", "Rather not"],
        [
            #OPT 0 Successes
            [
                [
                    lambda context: context["toggleMenu"]("Shop"),
                    ""
                ],
                [
                    lambda context: context["toggleMenu"]("Shop"),
                    "You werent convincing enough, and so your bargain was met by a counter-offer and you paid double the price for some old stale bread"
                ]
            ],
            #OPT 1 Successes
            [
                [
                    lambda context: None,
                    "You've beaten every single merchant to a pulp, that ought to buy you a bad reputation"
                ],
                [
                    lambda context: None,
                    "You werent convincing enough, and so your bargain was met by a counter-offer and you paid double the price for some old stale bread"
                ]
            ],
        ],
        [        
            #OPT 0 Failures
            [
                [
                    lambda context: lambda context: context["toggleMenu"]("Shop"),
                    "You werent able to come to an agreement with the merchants, they did throw a couple of rocks at you while they were fleeing the scene"
                ],
                [
                    lambda context: lambda context: context["toggleMenu"]("Shop"),
                    "You angered the merchants, they left without making you a deal"
                ]
            ],
            #OPT 1 Failures
            [
                [
                    lambda context: None,
                    "You werent able to come to an agreement with the merchants, they did throw a couple of rocks at you while they were fleeing the scene"
                ],
                [
                    lambda context: None,
                    "You angered the merchants, they left without making you a deal"
                ]
            ],
        ]
        ,8
    ),
    Event("You come across a group of merchants, they carry all kinds of goods but most importantly food",
        (5,7),
        "What do you do?",
        ["Bargain", "Rob them"],
        [
            #OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-10, "hp": lambda x: x+context["player"].max_hp*0.15}),
                    "You've successfully traded for some nourishing food"
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-30, "hp": lambda x: x+context["player"].max_hp*0.025}),
                    "You werent convincing enough, and so your bargain was met by a counter-offer and you paid double the price for some old stale bread"
                ]
            ],
            #OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+50, "hp": lambda x: x+context["player"].max_hp*0.2, "gre": 2}),
                    "You've beaten every single merchant to a pulp, that ought to buy you a bad reputation"
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+10, "hp": lambda x: x+context["player"].max_hp*0.055, "gre": 1}),
                    "Turns out the merchants were some seasoned warriors, they did not go out without a fight, you still get some healing and gold"
                ]
            ],
        ],
        [        
            #OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.02}),
                    "You werent able to come to an agreement with the merchants, they did throw a couple of rocks at you while they were fleeing the scene"
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"chr": -1}),
                    "You angered the merchants, they left without making you a deal"
                ]
            ],
            #OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.2, "gd": lambda x: x-x/2, "gre": 2}),
                    "You instantly tried to rob them but you slipped and they kick you repeatedly in the floor, they also rob you"
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"chr": -2, "gre": 4}),
                    "You try to rob them, turns out they had a Blessed Golem to protect them, you know you dont stand a chance so you retreat, they will remember that"
                ]
            ],
        ]
        ,8
    ),
    Event(
        "A wandering healer approaches you offering aid in exchange for a small token.",
        (0,5),
        "Do you accept the healer’s offer?",
        ["Accept", "Refuse"],
        [
            #OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.3, "vit": 1}),
                    "The healer channels ancient magic, restoring you beyond expectation."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.069}),
                    "The healer patches your wounds with practiced hands."
                ]
            ],
            #OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"lck": 1}),
                    "You refuse politely, but the healer blesses you anyway for courtesy."
                ],
                [
                    lambda context: None,
                    "You refuse the offer and move on."
                ]
            ],
        ],
        [
            #OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.025, "gd": lambda x: x-30}),
                    "The healer insists you *must* pay for wasting their time."
                ],
                [
                    lambda context: context["player"].addStatusEffect(OverTimeEffects(context["player"],3,effects={"hp": (-25,2)})),
                    "The healer was actually a witch. She curses you"
                ]
            ],
            #OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"chr": -1}),
                    "Your rude refusal offends the healer."
                ],
                [
                    lambda context: context["player"].addStatusEffect(OverTimeEffects(context["player"],3,effects={"gd": (-15,2)})),
                    "You refuse and the healer spits at you, hexing your coins."
                ]
            ],
        ],
        9
    ),
    Event(
        "A hidden spring glows under the moonlight, radiating gentle warmth.",
        (0,),
        "Do you bathe in the waters?",
        ["Enter the Spring", "Collect Water"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.2}),
                    "The waters heal your wounds almost instantly."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1, "hp": lambda x: x+context["player"].max_hp*0.15}),
                    "You emerge reinvigorated and healthier."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+40}),
                    "The bottled water will fetch a great price."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1}),
                    "You preserve a small sample that boosts your clarity."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.02}),
                    "You slip slightly but still enjoy some healing."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "You don’t gain much, but the warmth strengthens you."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+10}),
                    "You spill most of the water, but save a bit and sold it."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.015}),
                    "The bottle cracks and spills on the floor, as a last effort you lick the floor and heal a bit"
                ]
            ]
        ],
        8
    ),
    Event(
        "A shimmering spirit appears on the path, offering to share wisdom.",
        (2,0,1),
        "Do you listen to its guidance?",
        ["Accept Guidance", "Ask for a Blessing"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"int": 1, "mnd": 1}),
                    "You learn profound truths about the world."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1, "chr": 1}),
                    "Its teachings enlighten and inspire you."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.155}),
                    "A soothing light restores your strength."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "A protective aura settles in your body."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1}),
                    "The spirit’s message is vague, but still uplifting."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1}),
                    "You gain only a hint of insight, but feel encouraged."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.025}),
                    "The blessing is weak, but still helpful."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "The spirit touches you briefly, strengthening you lightly."
                ]
            ]
        ],
        7
    ),

]

# Events that arent inherently good or bad
neutralEvents = [
    Event(
        "You come across an abandoned library, and there is a book that's caught your attention, what do you do?",
        (6,2),
        "Investigate Book?",
        ["Open it", "Inspect it"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"lck": 2, "mnd": 2}),
                    "You uncover a lost grimoire. The arcane symbols resonate with you, granting deep insight."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"lck": 1, "mnd": 1}),
                    "The book is ancient knowledge. You learn a few useful things."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+40}),
                    "Inside the book you discover old coins of high value."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+20}),
                    "The book has a hidden compartment with a small pouch of coins."
                ]
            ],
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: None,
                    "It was just a regular book about elven anatomy."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.325, "awe": -1}),
                    "It was a mimic. It snapped at your hand and took a chunk of flesh."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": -1}),
                    "The book releases a cursed whisper cloud. You feel mentally foggy."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.2}),
                    "A magical trap triggers and blasts your face with force energy."
                ]
            ],
        ],
        11
    ),
    Event(
        "A small abandoned shrine sits by the road, covered in moss and silence.",
        (2,6),
        "Do you examine it?",
        ["Search Offering Box", "Clean the Shrine"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+15}),
                    "You find a few forgotten coins."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1}),
                    "You discover old inscriptions and gain insight."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "Cleaning it brings a sense of calm and vitality."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.01}),
                    "You feel serene after restoring a bit of its dignity."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.01}),
                    "A loose stone falls on your hand."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-10}),
                    "The offering box collapses, revealing nothing but costing you time and coin."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.009}),
                    "A sharp twig cuts your hand as you clean the structure."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1}),
                    "Something in the dust irritates your lungs."
                ]
            ]
        ],
        12
    ),
    Event(
        "A traveling merchant waves at you, offering curious trinkets.",
        (0,1),
        "Do you browse his wares?",
        ["Inspect Goods", "Chat with Merchant"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-10}),
                    "You buy a minor charm. It might be useful someday."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1, "gd": lambda x: x-5}),
                    "You identify a simple but instructive talisman."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1}),
                    "You gain conversational insight and improve your charm."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1}),
                    "His stories teach you something new about the world."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-20}),
                    "You get overcharged for junk."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.005}),
                    "You cut yourself on a poorly crafted trinket."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"chr": -1}),
                    "The merchant mocks your awkward small talk."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": -1}),
                    "His tall tales confuse you more than they enlighten."
                ]
            ]
        ],
        10
    ),
    Event(
        "You stumble upon a recently abandoned campsite. The embers are still warm.",
        (1,2),
        "Do you look around?",
        ["Search Tents", "Check the Perimeter"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x+20}),
                    "You find a small pouch of coins left behind."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": 1}),
                    "You discover notes with useful travel tips."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "You notice fresh tracks and gain awareness of the area."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x+context["player"].max_hp*0.012}),
                    "You find medicinal herbs growing along the perimeter."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.009}),
                    "A rusty pan collapses on your foot."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-10}),
                    "You accidentally tear a tent and compensate with coin."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1}),
                    "You twist your ankle on uneven ground."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"mnd": -1}),
                    "You misinterpret the tracks and feel unsure about your surroundings."
                ]
            ]
        ],
        11
    ),
]


#Events that are bad yet can end good
badEvents = [
    Event(
        "",
        (4,),
        "",
        ["",""],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: context["toggleEvent"](0),
                    "You break the trap and overpower the thieves, taking their belongings."
                ],
                [
                    lambda context: context["toggleEvent"](1),
                    "You escape and beat them down, grabbing a handful of gold."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: context["toggleEvent"](0),
                    "You convince the thieves you're worth more alive. They let you go and even give you a cut."
                ],
                [
                    lambda context: context["toggleEvent"](1),
                    "Your words soften them. You are released without harm."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: context["toggleEvent"](1),
                    "You struggle but fail. The trap tightens and bruises your body."
                ],
                [
                    lambda context: context["toggleEvent"](2),
                    "You thrash violently, angering the thieves. They beat you severely."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: context["toggleEvent"](1),
                    "Your negotiation fails. The thieves force you to pay for your freedom."
                ],
                [
                    lambda context: context["toggleEvent"](2),
                    "Your voice cracks. They mock you and kick you repeatedly."
                ]
            ],
        ],
        14
    ),
    Event(
        "You've fallen into a trap, you now find yourself at the mercy of thieves, what will you do?",
        (3,0,2),
        "Do you struggle?",
        ["Struggle", "Negotiate"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"str": 2, "gd": lambda x: x+60}),
                    "You break the trap and overpower the thieves, taking their belongings."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"str": 1, "gd": lambda x: x+35}),
                    "You escape and beat them down, grabbing a handful of gold."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1, "gd": lambda x: x+20}),
                    "You convince the thieves you're worth more alive. They let you go and even give you a cut."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1}),
                    "Your words soften them. You are released without harm."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.1}),
                    "You struggle but fail. The trap tightens and bruises your body."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.3}),
                    "You thrash violently, angering the thieves. They beat you severely."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"gd": lambda x: x-40}),
                    "Your negotiation fails. The thieves force you to pay for your freedom."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.15}),
                    "Your voice cracks. They mock you and kick you repeatedly."
                ]
            ],
        ],
        15
    ),
    Event(
        "A foul odor rises from a murky river. As you get closer, toxic fumes overwhelm you.",
        (1,4),
        "Do you investigate anyway?",
        ["Press Forward", "Retreat"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: (modifyAttrs(context["player"],{"vit": 1}),context["player"].addStatusEffect(OverTimeEffects(context["player"],4,effects={"hp": (-5,2)}))),
                    "You resist the fumes, gather useful herbs nearby, but suffer mild poisoning."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1, "hp": lambda x: x-context["player"].max_hp*0.2}),
                    "You find a rare, toxin-resistant plant, though your lungs burn."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.005}),
                    "You retreat with minor nausea."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.01}),
                    "You step back coughing, but avoid serious harm."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.25}),
                    "The fumes overwhelm you. You collapse, coughing blood."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.3}),
                    "Your curiosity nearly kills you as your lungs burn violently."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.0089}),
                    "You panic and breathe in deeply, inhaling a toxic cloud."
                ],
                [
                    lambda context: (modifyAttrs(context["player"],{"vit": -1}), context["player"].addStatusEffect(OverTimeEffects(context["player"],4,effects={"hp": (-15,2)}))),
                    "Your retreat is clumsy and slow; the fumes cling to you."
                ]
            ]
        ],
        16
    ),
    Event(
        "A pack of wolves circles you silently, their glowing eyes fixed on you.",
        (3,1,0,2),
        "Do you try to scare them away?",
        ["Fight", "Intimidate"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"str": 1, "hp": lambda x: x-context["player"].max_hp*0.005}),
                    "You fend off the wolves with raw strength, suffering light wounds."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"str": 1, "gd": lambda x: x+25}),
                    "You drive them away and claim a small stash hidden under their den."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1}),
                    "Your roar forces them to back down cautiously."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"chr": 1, "hp": lambda x: x-context["player"].max_hp*0.008}),
                    "You intimidate them, but not before one nips your leg."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.22}),
                    "They overpower you, tearing at your limbs."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.35}),
                    "You slip on wet leaves and are badly mauled."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.06}),
                    "Your attempt to intimidate only angers them. They pounce."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.18}),
                    "Your voice cracks comically. The wolves attack mercilessly."
                ]
            ]
        ],
        17
    ),
    Event(
        "A deep rumble shakes the cavern you're exploring. Rocks begin to fall.",
        (3,0,2,1),
        "Do you try to escape?",
        ["Sprint Out", "Brace Yourself"],
        [
            # OPT 0 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.008}),
                    "You dash through falling debris, taking only minor hits."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"str": 1, "hp": lambda x: x-context["player"].max_hp*0.07}),
                    "You break through a narrow exit, bruised but alive."
                ]
            ],
            # OPT 1 Successes
            [
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1, "hp": lambda x: x-context["player"].max_hp*0.0869}),
                    "You shield yourself, reducing the damage as the rocks fall."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": 1}),
                    "You withstand the impact surprisingly well."
                ]
            ]
        ],
        [
            # OPT 0 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.14}),
                    "A large boulder crushes your side as you try to escape."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.26}),
                    "The ground collapses under you; you're severely injured."
                ]
            ],
            # OPT 1 Failures
            [
                [
                    lambda context: modifyAttrs(context["player"],{"hp": lambda x: x-context["player"].max_hp*0.099}),
                    "Your stance fails and rocks slam into your back."
                ],
                [
                    lambda context: modifyAttrs(context["player"],{"vit": -1, "hp": lambda x: x-context["player"].max_hp*0.222}),
                    "Your bracing position collapses, causing heavy damage."
                ]
            ]
        ],
        18
    ),
]
