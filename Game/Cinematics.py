class Cinematic:
    def __init__(self, player, target, id, condition, npc):
        self.id = id
        self.player = player
        self.target = target
        self.condition = condition
        self.value = False
        self.begin = False
        self.finish = False
        self.moved = False
        self.end_dialogue = False
        self.npc = npc

    def update(self):
        if self.finish:
            self.npc.talking = False
            self.npc.in_cinematic = False
            return
        self.value = eval(self.condition)
        if self.value:
            self.npc.in_cinematic = True
            self.npc.talking = True