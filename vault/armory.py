from funcionalidades import Item, Weapon, MagicWeapon, Armor 
 
blacksmith = [Weapon("Sword", 500), 
              Weapon("Axe", 500), 
              Weapon("Griefreaver", 500),
              MagicWeapon("Cogheart Repeater", 10, 500),              
              MagicWeapon("Staff", 500, 30), 
              MagicWeapon("Stormweaver", 5, 100),
              Armor("Chestplate",0.04),
              Armor("Wardens Barkplate", 0.08)
              ]

bl_length = len(blacksmith)
