import libtcodpy as libtcod

line_directions = {
                    (0,1):"|", (1,0):'-', (0,-1):'|', (-1,0):'-',
                    (1,1):"\\",(-1,1):'\\',(1,-1):'/',(-1,-1):'/',
                    }

class Particle:
    def __init__(self,x,y,decay_time,color,cell,ticker,con):
        self.decay_time = decay_time
        self.color = color
        self.char = cell
        self.ticker = ticker
        self.x = x
        self.y = y
        self.con = con
        self.misc = None
        self.ai = None
        self.ticker.schedule_turn(1,self)
        
    def destroy_particle(self,game):
        self.ticker.remove_object(self)
        game.particles.remove(self)
        self.clear(game.gEngine)
        
    def use(self,game):
        if self.decay_time <= 0:
            self.destroy_particle(game)
        else:
            self.ticker.schedule_turn(1,self)
            self.decay_time -=1
        
    def draw(self,fov_map,gEngine,force_display=False):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color and then draw the character that represents this object at its position
            h,s,v = gEngine.console_get_char_background(self.con,self.x,self.y)
            col = libtcod.Color(0,0,0)
            libtcod.color_set_hsv(col,h,s,v)
            fr,fg,fb = self.color
            br,bg,bb = col
            gEngine.console_put_char_ex(self.con,self.x,self.y,self.char,fr,fg,fb,br,bg,bb)#self.char,self.color,col)
 
    def clear(self,gEngine):
        #erase the character that represents this object
        gEngine.console_set_char(self.con, self.x, self.y, ' ')    
    
        
def line_effect():
    pass
     
def path_effect(game,ox,oy,dx,dy,decay_time):
    libtcod.path_compute(game.path,ox,oy,dx,dy)
    px,py = ox,oy
    while not libtcod.path_is_empty(game.path):
        x,y = libtcod.path_walk(game.path,True)
        cell = line_directions[(px-x,py-y)]
        px,py = x,y
        p = Particle(x,y,decay_time,libtcod.yellow,cell,game.ticker,game.con)
        game.particles.append(p)
        
def explosion():
    pass
    
def nova():
    pass
    