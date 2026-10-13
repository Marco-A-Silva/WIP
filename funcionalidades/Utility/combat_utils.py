from enum import IntEnum

class Stats(IntEnum):
    CON, MND, INT, STR, AGI, LCK = range(6)


def modifyAttrs(target, changes: dict):
    for attr, val in changes.items():  
        holder = target.statBlock if attr.upper() in Stats.__members__ else target

        sign, value = val[0], val[1]
        current = getattr(holder, attr)

        match sign:
            case "=":
                setattr(target, attr, value)
            case "+":
                setattr(target, attr, current + value)
            case "-":
                setattr(target, attr, current - value)
                


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
        """

        self.turns = turns
        self.target = target
        self.effects = effects
        self.tags = tags

        for attr, (val,_) in effects.items():
            if _ == 1:
                self.og_stat = getattr(target,attr)
            elif _ == -1:
                self.og_turns = turns
            elif _ == 3:
                self.treshold = treshold  



        # Aplica todos los efectos al crear el objeto
        modifyAttrs(target, {attr: val for attr, (val,_) in effects.items() if _ == 0 or _ == 1})
    
    def passTurn(self):
        self.turns -= 1
        self.resolveOTE()

    def resolveOTE(self, trigger: int = False, hp:int = 0, mod: int = 0):
        # Revierte todos los efectos
        for attr, (val, nature) in self.effects.items():
            match nature:
                case -1: #Delayed Time Effect
                    if self.turns == 0:
                        attr = attr.replace("_fin","")
                        effects = {attr: (val,1)}
                        self.target.addStatusEffect(OverTimeEffects(self.target, self.og_turns, effects))
                case 0: #Permanent effect
                    pass
                case 1: #Limited time effect
                    if self.turns == 0: 
                        op = {"=": "=", "+": "-", "-": "+"}

                        val = (op[val[0]], self.og_stat)
                        modifyAttrs(self.target, {attr: val})
                case 2: #Every turn for X turns
                    modifyAttrs(self.target, {attr: val})
                case 3: #Triggered effect
                    if trigger:
                        tr = getattr(self.target, attr)
                        if tr <= self.treshold:
                            modifyAttrs(self.target, {attr: val})

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

                        final_value = round(old + delta*val)

                        # Si delta > 0 → se intentó curar → cancelar
                        if delta < 0:
                            setattr(self.target, f"_{attr}", final_value)
        