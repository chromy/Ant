'''
Displays a simulation of Langton's ant; a cellular automata
see http://en.wikipedia.org/wiki/Langton's_ant
'''
import random
import ConfigParser 
import pygame 
from pygame.locals import * 
import pgu.engine as engine #Hopefully replace this eventually
import simulation


BINDINGS = {('key','r'):''
            }

# TODO: Move all to settings
FPS_TARGET = 60
COLOR_ANT = (255,0,0)
COLOR_ON = (0,0,0)
COLOR_OFF = (255,255,255)

class AntGame(engine.Game):
    def __init__(self, fpslimit):
        self.heldkeys = set() # To remember what keys are being held down
        self.clock = pygame.time.Clock()
        self.fpslimit = fpslimit # Try to run at this speed
        self.fps = 0
    
    def tick(self):
        self.fps = self.clock.tick(self.fpslimit)
    
    def event(self,e):
        if e.type is QUIT: 
            self.state = engine.Quit(self)
            return True
    
        if e.type is KEYDOWN:
            self.heldkeys.add(e.key)
        elif e.type is KEYUP:
            try:
                self.heldkeys.remove(e.key)
            except KeyError:
                # Happens if key is held then window minimised then released
                # Maybe we should use theset.discard() and ignore this?
                # Or capture minimise events and clear held keys?   
                print 'ERROR: heldkey', e.key
            
        return False
 
class Sim(engine.State):
    def init(self):
        self.themap = simulation.Map() # Create the simulation grid
        self.ant = simulation.Ant((0,0), self.themap.getpoint, self.themap.setpoint) # Create ant at 0,0
        self.dirty = []
        self.speed = 0
        self.counter = 0
        self.gen = 0
        self.scale = 1
        self.offset = (-100,-100) # Put ant closer to middle TODO: should work this out from size
        self.simulate = True # Paused or not?
        self.redraw = False
        self.middle = (0,0)
        
        self.keybind = {'R':self.randcen,
                        'r':self.setredraw,
                        'S':self.reset,
                        's':self.togglesim,
                        'M':self.decspeed,
                        'm':self.incspeed,
                        }
        self.direct = {K_UP:(0,-1),
                       K_RIGHT:(1,0),
                       K_DOWN:(0,1),
                       K_LEFT:(-1,0),
                       }
    
    def paint(self, s):
        self.s = s
        self.sa = pygame.PixelArray(self.s)
        self.redraw = True
        self.update(s)

    def update(self, s):
        if self.redraw == False:
            changes = self.themap.getchanges()
            changes.extend(self.dirty)
            self.dirty = []
            self.drawchanges(changes)
            pos = self.drawant(self.ant) #Draw ant
            changes.append(pos)
            self.updatewindow(changes)
        else:
            # Draw and display whole screen
            self.drawant(self.ant)
            self.drawgrid()
            pygame.display.flip()
            self.redraw = False
            
 
    def updatewindow(self, changes):
        rect = None
        changes = [self.gridtoscreen(pos) for pos in changes]
        if len(changes) == 0:
            pass #No changes: don't update anything
        elif len(changes) == 1:
            c = changes[0]
            rect = pygame.Rect(c[0]-1,c[1]-1,2+self.scale,2+self.scale)
        elif len(changes) < 500:
            # If we have many changes make find a rect that covers everything then update
            xs, ys = map(None, *changes) #takes (x1,y1) (x2,y2) (x3,y3) gives (x1,x2,x3) (y1,y2,y3) 
            left, top = min(xs)-1, min(ys)-1
            width, height = max(xs)-left+3+self.scale, (max(ys)-top+3+self.scale)
            rect = pygame.Rect(left, top, width, height)
        
        if rect == True:
            pygame.display.update(rect)
        elif len(changes) == 0:
            pass
        else:
            pygame.display.flip()
            
    
    def gridtoscreen(self, pos):
        ox, oy = self.offset
        x, y = pos
        rx, ry = (self.scale*x)-ox, (self.scale*y)-oy
        return rx, ry
    
    def drawchanges(self, changes):
        changes = list(set(changes))
        for c in changes:
            state = self.themap.getpoint(c)
            col = COLOR_ON if state == True else COLOR_OFF
            coor = self.gridtoscreen(c)
            self.setpoint(coor, col)
            
    def drawant(self, theant):
        pos = theant.pos # Get position of ant (on grid)
        coor = self.gridtoscreen(pos) # Convert to screen coors
        self.setpoint(coor, COLOR_ANT) # Set that point
        self.dirty.append(pos) # Next draw update that spot
        return pos
            
    def drawgrid(self):
        self.s.fill(COLOR_OFF) # Blank screen
        cells = self.themap._grid # Get all 'on' cells 
        col = COLOR_ON
        for pos in cells: # Draw all cells
            coor = self.gridtoscreen(pos)
            self.setpoint(coor, col)
              
    def setpoint(self, coor, col):
        x, y = coor
        maxx = x + self.scale; maxy = y + self.scale #Get max set coors 
        sx, sy = self.s.get_size() #Get limits on screen size
        if (maxx <= sx) and (maxy <= sy) and (x >= 0) and (y >= 0): 
            if self.scale == 1:
                # If one pixel to box set pixel
                self.sa[x][y] = col 
            else:
                # Else draw rect of required size 
                rect = pygame.Rect(x,y,self.scale,self.scale)
                pygame.draw.rect(self.s, col, rect)
        
    def loop(self):
        for key in self.game.heldkeys:
            if key in self.direct: # Check arrow keys
                x, y = self.direct[key]
                self.middle = self.middle[0]+x, self.middle[1]+y # Change middle
                self.center() # Calculate offset
                self.redraw = True # Force full redraw as screen has moved relative to grid
        
        if self.simulate == True:
            if self.speed >= 0:
                cycles = self.speed + 1
            
            # Somewhat ugly hack for slow speeds (less than one cycle per frame)        
            else:
                # If the counter is larger then abs(speed) do one cycle else inc counter
                if self.counter > abs(self.speed)+1: 
                    self.counter = 0   
                    cycles = 1
                else:
                    self.counter += 1
                    cycles = 0
            
            # Do as many cycles as required
            for x in range(cycles):
                self.gen += 1
                self.ant.step()
    
    def event(self, e):
        if e.type == KEYDOWN:
            if e.key <= 255:
                letter = chr(e.key)
                # If shift is down upper case letter
                letter = letter.upper() if ((e.mod & KMOD_SHIFT) > 0) else letter
                # Call key binding if there is one
                try:
                    self.keybind[letter]()
                except KeyError:
                    pass
            
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: # Mouse wheel forward
                self.changescale(1)
            elif e.button == 5: # Mouse wheel out
                self.changescale(-1)

                
    def center(self, pos=None):
        """Calculates and sets correct offset from middle"""
        pos = self.middle if pos == None else pos
        px, py = pos
        sx, sy = self.s.get_size()
        sx, sy = sx/2, sy/2
        ox, oy = (px*self.scale) - sx, (py*self.scale) - sy
        self.offset = ox, oy
    
    def changescale(self, change):
        self.scale = abs((self.scale + change)) 
        self.scale = 1 if self.scale == 0 else self.scale
        self.center()
        self.redraw = True # Force redraw
        
    def reset(self):
        self.themap.clear()
        self.ant.pos = (0,0)
        self.ant.face = 1
        
    def randcen(self):
        # Randomly fill a 50x50 square in centre of grid
        # Maybe log seed here?
        for i in range(-25, 25):
            for j in range(-25, 25):
                tmp = random.randint(0,1)
                self.themap.setpoint((i,j), tmp)
    
    def incspeed(self):
        self.speed += 1
        
    def decspeed(self):
        self.speed -= 1
        
    def togglesim(self):
        self.simulate = not self.simulate
        
    def setredraw(self):
        self.redraw = True

def getsetings(path):
    """Get settings from config file. Currently only
    gets screensize"""
    config = ConfigParser.SafeConfigParser()
    config.read(path)
    screensize = config.get('basic','screensize')
    screensize = screensize.split(',')
    screensize = int(screensize[0]), int(screensize[1])
    return screensize

def main():
    pygame.init() #initialize pygame
    size = getsetings('settings.cfg') 
    pygame.display.set_mode(size)
    pygame.display.set_caption('Ant')
    g = AntGame(FPS_TARGET) 
    s = Sim(g)
    g.run(s, pygame.display.get_surface())
    


if __name__ == '__main__':
    main()
    
    