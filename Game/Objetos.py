from .Items import *

class Regadera(Tool):
    def __init__(self, agua):
        Tool.__init__(self, "regadera", 6, 0)
        self.agua = agua

    def regar(self):
        if self.agua >= 1:
            self.agua -= 1

#OBJETOS ACUMULABLES
SEMILLA = Item_acum("semilla", 2)
MADERA = Item_acum("Madera", 1)
PIEDRA = Item_acum("Piedra", 3)

#HERRAMIENTAS
PICO = Tool("Pico", 10, 5, materiales=[Craft_Item(MADERA, 5)])
AZADA = Tool("Azada", 8, 1, materiales=[Craft_Item(PIEDRA, 5), Craft_Item(MADERA, 10)])
HACHA = Tool("hacha", 5, 1)
REGADERA = Regadera(5)