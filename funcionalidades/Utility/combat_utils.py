

STATS = {"vit": 0, "mnd": 1, "int": 2, "str": 3, "lck": 4, "chr": 5, "awe": 6, "gre": 7,"end":8,"dex":9}

def modifyAttrs(target, changes: dict):

    for attr, val in changes.items():   
        if attr in STATS: attr = STATS[attr]
        if type(attr) == int:
            target.statBlock[attr] += val
        else:
            if hasattr(target, attr):
                # Si el valor es callable (función), lo ejecuta con el valor actual
                if callable(val):
                    setattr(target, attr, val(getattr(target, attr)))
                else:
                    setattr(target, attr, val)

def exec_apply_ote(hook, ctx):
    target = ctx["target"]

    effects = {}

    for mod in hook.params.get("mods", []):
        attr = mod["attr"]
        value = mod["value"]
        type = mod.get("type", 1)

        effects[attr] = (value, type)

    ote = OverTimeEffects(target,hook.params["turns"],effects={effects})
    target.addStatusEffect(ote)

def exec_modify_attr(hook, ctx):
    target = ctx["target"]

    effects = {}

    for mod in hook.params.get("mods", []):
        attr = mod["attr"]
        value = mod["value"]

        effects[attr] = value

    modifyAttrs(target,effects)
    
    return

ACTION_EXECUTORS = {
    "ote": exec_apply_ote,
    "attr": exec_modify_attr
}


class Hook:

    """Hook("on_hit","attr",main_weapon,enemy2,{mods: [{"attr": "hp", "value": -20}], "type": 2}
    This is an on-hit effect that reduces the enemy HP by 20 for 2 turns"""

    def __init__(self, type, action, params = {}, persistent = True, origin = None):
        self.type = type
        self.action = action
        self.persistent = persistent
        self.params = params
        self.origin = origin

    def run(self, ctx):
        ACTION_EXECUTORS[self.action](self, ctx)

class Hooks():
    def __init__(self):
        self._hooks = {}

    def add(self, type, hook):
        self._hooks.setdefault(type, []).append(hook)

    def run(self, type, ctx):
        for hook in self._hooks.get(type, []):
            hook.run(ctx)
            
    def remove(self, origin):
        for type, hooks in self._hooks.items():
            self._hooks[type] = [h for h in hooks if h.origin != origin]

class OverTimeEffects:
    def __init__(self, target, turns, effects, tags: str = "", treshold: int = 0):
        """
        effects: diccionario {atributo: (diferencia, naturaleza)}
        Ejemplo: {"hp": (-10,2), "armor": (-5,1)}
        """

        self.treshold = treshold
        self.turns = turns
        self.og_turns = turns
        self.target = target
        self.effects = effects
        self.tags = tags

        # Aplica todos los efectos al crear el objeto
        modifyAttrs(target, {attr: (lambda d=diff: (lambda x: x + d))() for attr, (diff,_) in effects.items() if _ == 0 or _ == 1})
    
    def passTurn(self):
        self.turns -= 1
        self.resolveOTE()

    def resolveOTE(self, trigger: int = False, hp:int = 0, mod: int = 0):
        # Revierte todos los efectos
        for attr, (diff, nature) in self.effects.items():
            match nature:
                case -1: #Delayed Time Effect
                    if self.turns == 0:
                        attr = attr.replace("_fin","")
                        effects = {attr: (diff,1)}
                        self.target.addStatusEffect(OverTimeEffects(self.target, self.og_turns, effects))
                case 0: #Permanent effect
                    pass
                case 1: #Limited time effect
                    if self.turns == 0: 
                        modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x - d))()})
                case 2: #Every turn for X turns
                    modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x + d))()})
                case 3: #Triggered effect
                    if trigger:
                        val = getattr(self.target, attr)
                        if val <= self.treshold:
                            modifyAttrs(self.target, {attr: (lambda d=diff: (lambda x: x + d))()})

                #Hooks       
                case 4: #Prevents increase of a stat
                    if trigger:
                        old = hp      # HP antes del cambio
                        new = mod     # HP después del cambio
                        delta = new - old

                        # Si delta > 0 → se intentó curar → cancelar
                        if delta > 0:
                            setattr(self.target, f"_{attr}", final_value)
                case 5: #Prevents descrease of a stat
                    if trigger:
                        old = hp      # HP antes del cambio
                        new = mod     # HP después del cambio
                        delta = new - old

                        final_value = round(old + delta*diff)

                        # Si delta > 0 → se intentó curar → cancelar
                        if delta < 0:
                            setattr(self.target, f"_{attr}", final_value)
        