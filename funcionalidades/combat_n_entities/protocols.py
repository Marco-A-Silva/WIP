from typing import Protocol

class Equipable(Protocol):
    name:str
    owner: 'Player'

    def setOwner(self, owner: 'Player') -> None: ...

    def equip(self) -> None: ... 