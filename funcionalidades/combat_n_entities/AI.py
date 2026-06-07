import random

class Action:

    tags = ["attack"]

    def possible_targets():
        return []

    def is_available():
        return

    def score():
        return

    def execute():
        return

class Attack(Action):
    type = "attack"

    def possible_targets(self, user, allies, enemies):
        return enemies

    def score(self, user, allies, enemies):
        best_score = -999
        best_target = None

        for target in self.possible_targets(user,allies,enemies):
            dmg = user.dmg * (1 - sum(piece.dmg_red for piece in target.armor.values() if piece is not None))

            if dmg > target._hp:
                s = 100
            else:
                s = dmg + (1 - target._hp/target.max_hp) * 20

            if s > best_score:
                best_score = s
                best_target = target

        return best_score, best_target

    def execute(self, user, allies, enemies, target):
        target.take_damage(user.dmg, False)

class UseSkill(Action):

    def __init__(self, skill):
        self.name = skill.name
        self.effect = skill.effect
        self.type = skill.type
        self.tags = skill.tags

    def possible_targets(self, user, allies, enemies):
        if self.type == "buff" or self.type == "heal":
            return allies + [user]
        if self.type == "special" or self.type == "debuff":
            return enemies

    def score(self, user, allies, enemies):
        best_score = -999
        best_target = None

        for target in self.possible_targets(user, allies, enemies):

            if self.type == "heal":
                s = (target.max_hp - target._hp) * 1.5
            elif self.type == "buff":
                s = 10 if target.hasStatus(self.tags) else 30
            elif self.type == "debuff":
                s = 0 if target.hasStatus(self.tags) else target._hp * 0.05 
            elif self.type == "special":
                dmg = 10
                s = 100 if dmg >= target._hp else dmg + (1 - target._hp / target.max_hp) * 20
            else:
                s = 0

            if s > best_score:
                best_score = s
                best_target = target

        return best_score, best_target


    def execute(self,user,allies,enemies,target):
        self.effect(user, target)

class EnemyAi:

    def __init__(self, actions, personality=None):
        self.actions = actions
        self.personality = personality or {
            "agression": 1.0,
            "caution": 1.0,
            "support": 1.0
        }

    def choose_action(self, user, allies, enemies):
        best_score = -999
        chosen_action = None
        chosen_target = None

        for action in self.actions:
            score, target = action.score(user, allies, enemies)

            if target is None:
                continue

            score = self.apply_personality(action, score)

            print(action.type, score)

            if score > best_score:
                best_score = score
                chosen_action = action
                chosen_target = target

        return chosen_action, chosen_target

    def apply_personality(self, action, score):
        if isinstance(action, Attack):
            score *= self.personality.get("agression", 1.0)

        elif isinstance(action, UseSkill):
            if action.type in ("special",):
                score *= self.personality.get("agression", 1.0)
            elif action.type in ("heal",):
                score *= self.personality.get("support", 1.0)
            elif action.type in ("buff",):
                score *= self.personality.get("caution", 1.0)
            elif action.type in ("debuff",):
                score *= self.personality.get("agression", 1.0)

        return score

    def act(self, user, allies, enemies):
        action, target = self.choose_action(user, allies, enemies)

        if action is None:
            return

        action.execute(user,allies,enemies,target)

        return {
            "enemy": user,
            "action": action,
            "target": target
        }
