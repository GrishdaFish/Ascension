import libtcodpy as libtcod
import random
import sys
#import psyco


try:
    import psyco
    psyco.full()
    psyco.log()
    psyco.profile()
    
except ImportError:
    pass

Game_Screen_Width = 100
Game_Screen_Height = 100

Message_Screen_Width = Game_Screen_Width - 2
Message_Screen_Height = Game_Screen_Height / 4
Message_V_Pos = Game_Screen_Height - Message_Screen_Height - 1

Stat_Screen_Width = Game_Screen_Width / 4
Stat_Screen_Height = Game_Screen_Height - Message_Screen_Height - 2
Stat_H_Pos = Game_Screen_Width - Stat_Screen_Width - 1

Game_Console_Width = Game_Screen_Width - Stat_Screen_Width 
Game_Console_Height = Game_Screen_Height - Message_Screen_Height -2

Inventory_Width = Game_Screen_Width - Stat_Screen_Width  -2
Inventory_Height = Game_Screen_Height - Message_Screen_Height -2

##Rewrite of the dungeon generator
class GenDungeon:
##========================================================================================================================
    def __init__(self,x,y,minrs=0,maxrs=0,mincl=0,maxcl=0,var=0,style='Square',maxRooms=0):
##========================================================================================================================
        ##Adding Game_Console_Width is a workaround for out of bounds indexing problem when drawing the map in the game
        ##This makes sure that there is an entire game screens width surrounding the map (Temp Fix)
        self.map_x = x*2#+(Game_Console_Width*2)##200x200 Generally produces a nice looking dungeon
        self.map_y = y*2#+(Game_Console_Width*2)##Note: Has to be square(for now atleast)
        self.map_arr = [["#" for col in range(self.map_x)] for row in range(self.map_y)]#x = down y = side
        
        self.variation = var ##percentage of room and corridor style variation. 0 is no variation, 100 would be constant variation
                             ##Default Corridor is 'Straight'
        self.style = style   ##Main style of room to generate. Only Square and Rectangle are done for now
        
        ##mins and maxes of rooms and corridor sizes
        if minrs == 0:
            self.min_room_size = x/20
        else:
            self.min_room_size = minrs
        if maxrs == 0:
            self.max_room_size = x/10
        else:
            self.max_room_size = maxrs
            
        if mincl == 0:
            self.min_cor_len = self.min_room_size#/2
        else:
            self.min_cor_len = mincl
        if maxcl == 0:
            self.max_cor_len = self.max_room_size#/2
        else:
            self.max_cor_len = maxcl
            
        self.cor_len = 0 #used later for keeping track of the length of a corridor for room placement 
        
        if maxRooms < 10:                                        #Overrides user settings if they try to generate too few rooms
            self.max_rooms = (self.map_x /self.max_room_size)*3  
        if maxRooms >= (self.map_x/self.max_room_size)*3:        #Overrides user settings if they try to generate too many rooms for the map and max room size
            self.max_rooms = (self.map_x /self.max_room_size)*3 
        if maxRooms >=10:                                        #Otherwise set rooms to user settings ;)
            self.max_rooms = maxRooms
            
        ##boundries to ensure rooms do not get generated outside of the array 
        self.xstart = (self.max_cor_len + self.max_room_size)+2#(Game_Console_Width +2)
        self.xend = self.map_x - (self.max_cor_len + self.max_room_size)-3#(Game_Console_Width -3)
        self.ystart = (self.max_cor_len + self.max_room_size)+2#(Game_Console_Width +2)
        self.yend = self.map_y - (self.max_cor_len + self.max_room_size)-3#(Game_Console_Width -3)
        
        
        self.genLayout()

##===============================================================================
    def genLayout(self):
##===============================================================================
        ##Notes -x = up +x = down, -y = Left +y = Right
        Cor,Picked,stairs_placed = False,False,False
        rooms = 1
        z = 0
        ##Build the first room in the center of the map
        s = self.map_x/2 -2
        e = s + random.randrange(self.min_room_size,self.max_room_size+1)
        for y in range(s,e):
            for x in range (s,e):    
                self.map_arr[x][y] = " "
        ##Then build the rest of the map
        while rooms <= self.max_rooms:             
            while Cor == False and Picked == False:
                ##Then we Pick a random wall, and direction for the corridor to go
                x_pick = random.randrange(self.xstart,self.xend)
                y_pick = random.randrange(self.ystart,self.yend)
                c_dir = random.randrange(0,11)#0-5 = x ,6-10 = y
                dir = random.randrange(0,11)#0-5 = -, 6-10 = + 
                self.cor_len = random.randrange(self.min_cor_len,self.max_cor_len+1)
                self.room_size = random.randrange(self.min_room_size,self.max_room_size+1)
                ##if picked cell is open space
                if self.map_arr[x_pick][y_pick] == " ":
                    ##check all cells surrounding it for placed corridors and/or rooms so we dont generate rooms ontop of other rooms (as much)
                    ##Some overlapping of rooms makes for more interesting dungeons
                    ##Should be able to make corridors longer to get less overlap
                    if dir <= 5:#up and left 
                        if c_dir <= 5: #up
                            for y in range(y_pick-(self.max_room_size/2),y_pick+(self.max_room_size/2)):##check side to side half the width of the largest size room
                                for i in range((x_pick-2)-self.max_cor_len,x_pick+1 ):##check the max length of a corridor
                                    if self.map_arr[i][y] == " ":
                                        z +=1
                        else:#left
                            for y in range(x_pick-(self.max_room_size/2),x_pick+(self.max_room_size/2)):
                                for i in range((y_pick-2)-self.max_cor_len,y_pick+1):
                                    if self.map_arr[y][i] == " ":
                                        z +=1
                    else: #down and right
                        if c_dir <= 5:#down 
                            for y in range(y_pick-(self.max_room_size/2),y_pick+(self.max_room_size/2)):
                                for i in range(x_pick+2,(x_pick+1)+self.max_cor_len+1):
                                    if self.map_arr[i][y] == " ":
                                        z +=1
                        else:#right
                            for y in range(x_pick-(self.max_room_size/2),x_pick+(self.max_room_size/2)):
                                for i in range(y_pick+2,(y_pick+1)+self.max_cor_len+1):
                                    if self.map_arr[y][i] == " ":
                                        z +=1
                    ##if yes, then generatate new numbers and start over                    
                    if z >= self.max_room_size:
                        z=0
                        Picked = False
                        x_pick = random.randrange(self.xstart,self.xend)
                        y_pick = random.randrange(self.ystart,self.yend)
                        self.cor_len = random.randrange(self.min_cor_len,self.max_cor_len+1)
                        self.room_size = random.randrange(self.min_room_size,self.max_room_size+1)
                        c_dir = random.randrange(0,11)#0-5 = x ,6-10 = y
                        dir = random.randrange(0,11)#0-5 = -, 5-10 = + 
                    ##otherwise continue onto drawing a corridor
                    else:
                        Picked = True
                        Cor = True 
            ##draw corridors and rooms
            if dir <= 5:#up and left
                if c_dir <= 5: #up
                    self.drawCorridor(1,x_pick,y_pick)##Draw the corridor
                    self.drawRoom(1,x_pick-(self.cor_len-1),y_pick+(self.room_size/2))##Place a room at the end of the corridor
                    
                if c_dir >=6:#left
                    self.drawCorridor(2,x_pick,y_pick)
                    self.drawRoom(2,x_pick+(self.room_size/2),y_pick-(self.cor_len-1))                    
                    
            if dir >=6:#down and right
                if c_dir <= 5:#down
                    self.drawCorridor(3,x_pick,y_pick)
                    self.drawRoom(3,x_pick+(self.cor_len+1),y_pick+(self.room_size/2))                    
                    
                if c_dir >=6:#right
                    self.drawCorridor(4,x_pick,y_pick)
                    self.drawRoom(4,x_pick-(self.room_size/2),y_pick+(self.cor_len+1))
            rooms +=1
            z = 0
            Cor = False
            Picked = False
        while stairs_placed == False:
            x_pick = random.randrange(self.xstart,self.xend)
            y_pick = random.randrange(self.ystart,self.yend)
            if self.map_arr[x_pick][y_pick] == " ":
                self.map_arr[x_pick][y_pick] = ">"
                stairs_placed = True
                break
                            #############
                            ##CORRIDORS##
                            #############
##===============================================================================
    def drawCorridor(self,dir,x,y):
##===============================================================================
        self.dir = dir
        self.x = x
        self.y = y
        types=['Straight']#,'Tee']#,'Cross','Pipe']##Add new CORRIDOR types here
        corridors={
                    'Straight' : self.strCor(),
                    'Tee'      : self.teeCor(),
                    'Cross'    : self.crossCor(),
                    'Pipe'     : self.pipeCor(),
                    ##Add new corridor methods here for style variation
                }
        r = random.randrange(1,100)
        if r > self.variation:
            corridors[types[0]]
        else:
            rc = random.choice(types)
            corridors[rc]
            
##===============================================================================
    def strCor(self):##'|' Corridor
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        if dir is 1:#up
            for i in range(x-(self.cor_len-1),x):#
                self.map_arr[i][y] = " "
                self.map_arr[i][y+1] = " "
            
        if dir is 2:#left
            for i in range(y-(self.cor_len-1),y):
                self.map_arr[x][i] = " "
                self.map_arr[x+1][i] = " "
                
        if dir is 3:#down
            for i in range(x,x+(self.cor_len+1)):
                self.map_arr[i][y] = " "
                self.map_arr[i][y+1] = " "
                
        if dir is 4:#right
            for i in range(y,y+(self.cor_len+1)):
                self.map_arr[x][i] = " "
                self.map_arr[x+1][i] = " "

##===============================================================================
    def teeCor(self):##'T' Corridor
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        if dir is 1:
            for i in range(x-(self.cor_len-1),x):
                self.map_arr[i][y] = " "            
            for i in range(y-(self.cor_len-1),y):
                self.map_arr[x-self.cor_len/2][i] = " "
            self.drawRoom(2,(x-self.cor_len/2)+(self.room_size/2),(y-self.cor_len))
            #self.drawRoom(2,x_pick+(self.room_size/2),y_pick-(self.cor_len-1))   
            
        if dir is 2:
            for i in range(y-(self.cor_len-1),y):
                self.map_arr[x][i] = " "
                
        if dir is 3:
            for i in range(x,x+(self.cor_len+1)):
                self.map_arr[i][y] = " "
            for i in range(y,y+(self.cor_len+1)):
                self.map_arr[x+self.cor_len/2][i] = " "
            self.drawRoom(4,(x+self.cor_len/2)-(self.room_size/2),(y+self.cor_len))   
 
        if dir is 4:
            for i in range(y,y+(self.cor_len+1)):
                self.map_arr[x][i] = " "
##===============================================================================
    def crossCor(self):##'+' Corridor
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        
##===============================================================================
    def pipeCor(self):##Bent at both ends kind of like a 'Z' :E
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        
        
                                #########
                                ##ROOMS##
                                #########
##===============================================================================
    def drawRoom(self,dir,x,y):
##===============================================================================
        self.dir = dir
        self.x = x
        self.y = y
        types=['Square','Rect']##Add new ROOM types here
        rooms = {
                    'Square' : self.drawSquareRoom(),
                    'Rect'   : self.drawRectRoom(),
                    ##Add new room methods here for style variation
                }
        r = random.randrange(1,100)
        if r > self.variation:
            rooms[self.style]
        else:
            rm = random.choice(types)
            rooms[rm]
            
        
##===============================================================================
    def drawSquareRoom(self):
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        if dir is 1:
            for yy in range((y-self.room_size),y+1):
                for xx in range ((x-self.room_size),x):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 2:
            for yy in range(y,y+self.room_size):
                for xx in range (x-self.room_size,x):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 3:
            for yy in range(y-self.room_size,y+1):
                for xx in range (x,x+self.room_size):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 4:
            for yy in range(y,y+self.room_size):
                for xx in range (x,x+self.room_size):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
        
##===============================================================================
    def drawRectRoom(self):##Needs double drawing options for rects going up/down or side/side regardless of direction
##===============================================================================
        dir = self.dir
        x = self.x
        y = self.y
        ysize = random.randrange(self.min_room_size,self.max_room_size+1)
        xsize = random.randrange(self.min_room_size,self.max_room_size+1)
        if dir is 1:
            for yy in range((y-ysize),y):                
                for xx in range ((x-xsize),x):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 2:
            for yy in range(y,y+ysize):
                for xx in range (x-xsize,x):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 3:
            for yy in range(y-ysize,y+1):
                for xx in range (x,x+xsize):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "
                    
        if dir is 4:
            for yy in range(y,y+ysize):
                for xx in range (x+1,x+xsize+1):
                    self.map_arr[xx][yy] = " "
                    self.map_arr[xx+self.room_size][yy+self.room_size] = " "

##===============================================================================
    def getMap(self):
##===============================================================================
        return self.map_arr

#Just for testing ;)
if __name__ == "__main__":
    Main_Console = libtcod.console_init_root(Game_Screen_Width,Game_Screen_Height,"Lost Horizon 0.0.1a",False)
    libtcod.sys_set_fps(25)
    map = GenDungeon(50,50,var=50)
    map_arr = map.getMap()
    pix = libtcod.image_new(len(map_arr),len(map_arr))
    for x in range(len(map_arr)):
        for y in range(len(map_arr)):
            if map_arr[x][y] == "#":
                libtcod.image_put_pixel(pix,x,y,libtcod.dark_grey)
            if map_arr[x][y] == " ":
                libtcod.image_put_pixel(pix,x,y,libtcod.white)
    while not libtcod.console_is_window_closed():
        #libtcod.image_blit(pix,0,50,50,libtcod.BKGND_SET,1.0,1.0,0.0)
        libtcod.image_blit_2x(pix,0,0,0)
        libtcod.console_flush()
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        if key.vk == libtcod.KEY_ESCAPE:
            break
    
    
    
    
    