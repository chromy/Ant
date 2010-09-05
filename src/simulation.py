
class Ant(object):
    def __init__(self, pos, getpoint, setpoint):
        self.dir = {0:(0,-1), 1:(1,0), 2:(0,1), 3:(-1,0)}
        self.face = 1
        self.pos = pos
        
        self.getpoint = getpoint
        self.setpoint = setpoint
        
    def step(self):
        x, y = self.pos
        if self.getpoint(self.pos) == True:
            self.face = (self.face + 1) % 4
        else:
            self.face = (self.face - 1) % 4
            
        self.setpoint(self.pos, not self.getpoint(self.pos))
        x = x + self.dir[self.face][0] 
        y = y + self.dir[self.face][1] 
        self.pos = x, y
        
class Map(object):
    def __init__(self):
        self._grid = set()
        self.backround = False
        self._changes = []

    def getpoint(self, pos):
        if pos in self._grid:
            return True
        else:
            return False
    
    def setpoint(self, pos, state):
        self._changes.append(pos)
        if state == True:
            self._grid.add(pos)
        else:
            self._grid.discard(pos)
    
    def getchanges(self):
        changes = self._changes
        self._changes = []
        return changes
    
    def clear(self, blank=False):
        self._changes.extend(self._grid)
        self._grid.clear()
                
    def invert(self):
        pass