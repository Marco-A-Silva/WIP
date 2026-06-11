import json, pygame, copy
from funcionalidades.combat_n_entities.combat_items import (
    Weapon, MagicWeapon, RangedWeapon, SecondaryWeapon, Armor
)
from vault import shopItems, enemySkills, magicSkills, meleeSkills


RACE_APTITUDES = {
    "Eudrýan": {

    },
    "Arcanthian": {

    },
    "Thanoran": {

    },        
    "Ünds": {

    },        
    "Apexian": {

    },        
    "Brumed": {

    },        
    "Thanoran": {

    },        
    "Thalûnd": {

    },
    "Skŷnder": {

    },
    "Ferravan": {

    },
    "Vitalean": {

    },
    "Noctyrrn": {

    },
}

def create_initial_save(race_name, save_path):
    races = {
        "Eudran": {
            "hp": 700, "mp": 30, "sta": 100,
            "weapon": {"name": "Rusty Iron Sword", "dmg": 30, "weight": 1, "skills": ["Focus Slash"]},
            "statBlock": generate_statblock(race_name)

        },
        "Arcanthian": {
            "hp": 400, "mp": 150, "sta": 40,
            "weapon": {"name": "Oak Staff", "dmg": 5, "mgc": 30, "mana_cost":20, "skills": ["Fireball"]},
            "statBlock": generate_statblock(race_name)
        },
        "Thanoran": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },        
        "Ünds": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },        
        "Apexian": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },        
        "Brumed": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },        
        "Thanoran": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },        
        "Thalûnd": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },
        "Skŷnder": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },
        "Ferravan": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },
        "Vitalean": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        },
        "Noctyrrn": {
            "hp": 500, "mp": 60, "sta": 80,
            "weapon": {"name": "Dagger", "dmg": 30,"weight": 0.5, "skills": ["Shadow Step"]},
            "statBlock": generate_statblock(race_name)
        }
    }

    c = races[race_name]

    data = {
        "room": 0,
        "load": True,
        "advParty": [{
            "player_hp": c["hp"],
            "player_max_hp": c["hp"],
            "player_mp": c["mp"],
            "player_max_mp": c["mp"],
            "player_sta": c["sta"],
            "player_max_sta": c["sta"],
            "player_statBlock": c["statBlock"],
            "weapon": c["weapon"],
            "armor": {},
            "items": ["Health Vial"]
        }],
        "enemies": []
    }

    with open(save_path, "w") as f:
        json.dump(data, f, indent=4)

def load_game_state(save_path):

    from funcionalidades.combat_n_entities.entities import Player, Enemy

    with open(save_path, "r") as f:
        data = json.load(f)

    room = data.get("room", 0)
    load = data.get("load")

    # -------- ENEMIES --------
    enemyList = []
    if data.get("enemies"):
        enemyList = [
            Enemy(
                e["name"],
                e["hp"],
                skills=[enemySkills[k] for k in e.get("skills", []) if k in enemySkills]
            )
            for e in data["enemies"]
        ]

    # -------- PLAYERS --------
    advParty = []

    for p in data["advParty"]:

        weapons = {"primary": None, "secondary": None}
        armor = {"head": None, "chest": None, "legs": None, "feet": None}

        # ----- PLAYER -----
        player = Player(
            load,
            p["player_hp"],
            p["player_mp"],
            p["player_sta"],
            max_hp=p["player_max_hp"],
            max_mp=p["player_max_mp"],
            max_sta=p["player_max_sta"],
            weapons=weapons,
            armor=armor,
            statBlock=p["player_statBlock"]
        )

        if p.get("armor"):
            pieces = p["armor"]
            for key, piece in pieces.items():
                if piece:
                    piece_eq = Armor(
                        piece["name"],
                        piece.get("dmg_red", 0),
                        piece["type"]
                    )

                    player.equip_armament(piece_eq,load)

        if p.get("weapon"):
            weaponss = p["weapon"]

            for key,weapon in weaponss.items():
                if weapon:
                    match weapon["type"][0]:
                        case "melee":
                            skills = {
                                k: (magicSkills.get(k) or meleeSkills.get(k))
                                for k in weapon.get("skills", [])
                                if k in magicSkills or k in meleeSkills
                            }

                            weapon_eq = Weapon(
                                weapon["name"],
                                weapon.get("dmg", 0),
                                weight=weapon.get("weight", 1),
                                type=weapon.get("type"),
                                skills=skills
                            )
                            player.equip_armament(weapon_eq,load)

                        case "magic":
                            skills = {
                                k: (magicSkills.get(k) or meleeSkills.get(k))
                                for k in weapon.get("skills", [])
                                if k in magicSkills or k in meleeSkills
                            }

                            weapon_eq = MagicWeapon(
                                weapon["name"],
                                weapon.get("dmg", 0),
                                weapon.get("mgc",0),
                                weight=weapon.get("weight", 1),
                                mana_cost=weapon.get("mana_cost",0),
                                type=weapon.get("type"),
                                skills=skills
                            )
                            player.equip_armament(weapon_eq,load)

                        case "ranged":
                            skills = {
                                k: (magicSkills.get(k) or meleeSkills.get(k))
                                for k in weapon.get("skills", [])
                                if k in magicSkills or k in meleeSkills
                            }

                            weapon_eq = RangedWeapon(
                                weapon["name"],
                                weapon.get("dmg", 0),
                                weapon.get("ammo", 1),
                                weapon.get("ammoReq", 1),
                                weight=weapons.get("weight", 1),
                                type=weapon.get("type"),
                                skills=skills
                            )
                            player.equip_armament(weapon_eq,load)

                        case "secondary":
                            skills = {
                                k: (magicSkills.get(k) or meleeSkills.get(k))
                                for k in weapon.get("skills", [])
                                if k in magicSkills or k in meleeSkills
                            }

                            weapon_eq = SecondaryWeapon(
                                weapon["name"],
                                weapon.get("dmg_red",0),
                                weapon.get("dmg", 0),
                                weapon.get("stat", 0),
                                weight=weapons.get("weight", 1),
                                type=weapon.get("type"),
                                skills=skills
                            )
                            player.equip_armament(weapon_eq,load)

        # ----- ITEMS -----
        for it in p.get("items", []):
            for shop_it, *_ in shopItems:
                if shop_it[0].name == it:
                    player.equip_armament(shop_it[0], False)

        advParty.append(player)

    return {"party": advParty, "enemies":enemyList, "room":room}

def generate_statblock(class_name):
    apt = CLASS_APTITUDES[class_name]
    stats = []

    for i in range(10):
        if i in apt.get("high", []):
            val = roll_stat(7, 11, "high")
        elif i in apt.get("low", []):
            val = roll_stat(0, 4, "low")
        else:
            val = roll_stat(3, 8)

        stats.append(val)

    return stats

def roll_stat(min_v, max_v, bias=None):
    """
    bias = None | "high" | "low"
    """
    if bias == "high":
        return random.choices(
            population=range(min_v, max_v + 1),
            weights=[i*i for i in range(1, max_v - min_v + 2)]
        )[0]

    if bias == "low":
        return random.choices(
            population=range(min_v, max_v + 1),
            weights=list(reversed([i*i for i in range(1, max_v - min_v + 2)]))
        )[0]

    return random.randint(min_v, max_v)


