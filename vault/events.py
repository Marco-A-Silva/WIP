from funcionalidades.Utility.combat_utils import OverTimeEffects, modifyAttrs
from funcionalidades.combat_n_entities.combat_items import Item
from vault.items import shopItems
import pygame, random

CON, MND, INT, STR, AGI, LCK = range(6)

class Event:
    def __init__(self, description, actions):
        self.description = description
        self.actions = actions

    def resolve(self, res, context):
        raise NotImplementedError