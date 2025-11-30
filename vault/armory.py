from funcionalidades import Item, Weapon, MagicWeapon, Armor 
 
blacksmith = [
    Weapon("Sword",  50), 
    Weapon("Axe", 80), 
    Weapon("Griefreaver", 100),
    MagicWeapon("Cogheart Repeater", 10, 70), 
    MagicWeapon("Staff", 5, 30), 
    MagicWeapon("Stormweaver", 5, 100),
    Armor("Chestplate",0.04),
    Armor("Wardens Barkplate", 0.08),
    Armor("Abyss Touched Carapace", 0.45)
]

bl_length = len(blacksmith)
