class Cinematic:
    def __init__(self, player, target, id, condition, npcs):
        self.id = id
        self.player = player
        self.target = target
        self.condition = condition
        self.value = False
        self.begin = False
        self.finish = False
        self.moved = False
        self.end_dialogue = False
        self.npcs = npcs
        self.npc = self.npcs[0]

    def update(self):
        if self.finish:
            self.npc.talking = False
            self.npc.in_cinematic = False
            return
        self.value = eval(self.condition)
        if self.value:
            self.npc.in_cinematic = True
            self.npc.talking = True

class Cinematic_manager:
    def __init__(self, cinematicas, camera, map):
        self.cinematicas = cinematicas
        self.cinematic_now = None
        self.camera = camera
        self.in_cinematic = False
        self.camera_can_move = False
        self.map = map

    def finish_cinematic(self):
        self.camera.player.can_move = True
        self.camera_can_move = False
        self.cinematic_now.finish = True
        self.in_cinematic = False
        self.camera.moved = False
        if self.cinematic_now in self.cinematicas:
            self.cinematicas.remove(self.cinematic_now)

    def update(self):
        for cinematica in self.cinematicas:
            cinematica.update()
            if cinematica.value:
                self.cinematic_now = cinematica
                self.camera.ajust_cinematic(self.cinematic_now)
                self.in_cinematic = True
                self.cinematic_now.begin = True