from funcionalidades import Item, Weapon, MagicWeapon, Armor 
from funcionalidades.combat_n_entities.combat_items import OverTimeEffects, modifyAttrs


meleeSkills = {
    "Focus Slash": lambda self, target: (target.take_damage(self.weapon.melee_dmg*1.30, False), modifyAttrs(self.weapon.owner, {"sta": lambda x: x-self.weapon.weight*20})),
}

magicSkills = {
    "Fireball": lambda self, target: target.addStatusEffect(OverTimeEffects(target, 3, effects= {"hp": (-25,2)}))
}

blacksmith = [
    Weapon("Sword", 50, weight=1.0, skills={"Focus Slash": meleeSkills["Focus Slash"]}),
    Weapon("Axe", 80, weight=1.4, skills={"Focus Slash": meleeSkills["Focus Slash"]}),
    Weapon("Griefreaver", 100, weight=2.0, skills={"Focus Slash": meleeSkills["Focus Slash"]}),
    Weapon("Great Hammer", 350, weight=3.0, skills={"Focus Slash": meleeSkills["Focus Slash"]}),

    MagicWeapon("Staff", 5, 30, mana_cost=10, skills={"Fireball": magicSkills["Fireball"]}),
    MagicWeapon("Cogheart Repeater", 10, 70, mana_cost=25, skills={"Fireball": magicSkills["Fireball"]}),
    MagicWeapon("Stormweaver", 5, 100, mana_cost=45, skills={"Fireball": magicSkills["Fireball"]}),
    MagicWeapon("Staff of ultimate power", 5, 250, mana_cost=60, skills={"Fireball": magicSkills["Fireball"]}),

    Armor("Chestplate", 0.04),
    Armor("Wardens Barkplate", 0.08),
    Armor("Abyss Touched Carapace", 0.45),
]

bl_length = len(blacksmith)