##Python prototype for the c++ pyd
##Basicly a wrapper around libtcod, like the pyd is
##Used incase the pyd is absent so the code wont break.
##pretty much a c++ port, not very pythonic, doesnt need to be.
##Might clean it up later

import libtcodpy as libtcod


class Tile:
    def __init__(self,x,y,cell,blocked,block_sight,explored,spawn_node):
        self.x=x
        self.y=y
        self.cell=cell
        self.blocked=blocked
        self.block_sight=block_sight
        self.explored=explored
        self.spawn_node=spawn_node
        
class gEngine:
    def __init__(self,w,h,name,fs,fps):
        libtcod.console_init_root(w,h,name,fs)
        libtcod.sys_set_fps(fps)
        
        self.mConsole=[]
        self.mMap=[]
        self.mImages=[]
        self.FOV = None
        self.color_dark_wall = libtcod.darker_grey
        self.color_light_wall = libtcod.Color(99,99,99)
        self.color_dark_ground = libtcod.dark_grey
        self.color_light_ground = libtcod.Color(125,125,125)
        self.color_tile_wall = libtcod.Color(177,177,177)
        self.color_tile_ground = libtcod.Color(190,190,190)
        
    def console_new(self,width,height):
        self.mConsole.append(libtcod.console_new(width,height))
        return len(self.mConsole)
        
    def console_remove_console(self,con):
        c = self.mConsole.pop(con-1)
        libtcod.console_delete(c)
        
    def console_get_height_rect(self,con,x,y,width,height,fmt):
        if con == 0:
            return libtcod.console_get_height_rect(con,x,y,width,height,fmt)
        else:
            return libtcod.console_get_height_rect(self.mConsole[con-1],x,y,width,height,fmt)
        
    def console_set_default_foreground(self,con,r,g,b):
        col = libtcod.Color(r,g,b)
        if con == 0:
            libtcod.console_set_default_foreground(con,col)
        else:
            libtcod.console_set_default_foreground(self.mConsole[con-1],col)
        
    def console_set_default_background(self,con,r,g,b):
        col = libtcod.Color(r,g,b)
        if con == 0:
            libtcod.console_set_default_background(con,col)
        else:
            libtcod.console_set_default_background(self.mConsole[con-1],col)
        
    def console_print_frame(self,con,x,y,width,height,clear):
        if con == 0:
            libtcod.console_print_frame(con,x,y,width,height,clear)
        else:
            libtcod.console_print_frame(self.mConsole[con-1],x,y,width,height,clear)
        
    def console_print_rect(self,con,x,y,width,height,fmt):
        if con == 0:
            libtcod.console_print_rect(con,x,y,width,height,fmt)
        else:
            libtcod.console_print_rect(self.mConsole[con-1],x,y,width,height,fmt)
        
    def console_blit(self,conSrc,xSrc,ySrc,wSrc,hSrc,conDest,xDest,yDest,foreAlph=1.0,backAlph=1.0):
        dest=None
        src = self.mConsole[conSrc-1]
        if conDest == 0:
            dest = 0
        else:
            dest = self.mConsole[conDest-1]
        libtcod.console_blit(src,xSrc,ySrc,wSrc,hSrc,dest,xDest,yDest,foreAlph,backAlph)
        
    def console_put_char_ex(self,con,x,y,chr,cr,cg,cb,br,bg,bb):
        fore = libtcod.Color(cr,cg,cb)
        back = libtcod.Color(br,bg,bb)
        if con ==0:
            libtcod.console_put_char_ex(con,x,y,chr,fore,back)
        else:
            libtcod.console_put_char_ex(self.mConsole[con-1],x,y,chr,fore,back)
        
    def console_set_char(self,con,x,y,chr):
        if con == 0:
            libtcod.console_set_char(con,x,y,chr)
        else:
            libtcod.console_set_char(self.mConsole[con-1],x,y,chr)
        
    def console_set_alignment(self,con,align):
        if con==0:
            libtcod.console_set_alignment(con,align)
        else:
            libtcod.console_set_alignment(self.mConsole[con-1],align)
        
    def console_print(self,con,x,y,fmt):
        if con == 0:
            libtcod.console_print(con,x,y,fmt)
        else:
            libtcod.console_print(self.mConsole[con-1],x,y,fmt)
        
    def console_flush(self):
        libtcod.console_flush()
        
    def console_clear(self,con):
        if con == 0:
            libtcod.console_clear(con)
        else:
            libtcod.console_clear(self.mConsole[con-1])
            
    def console_get_char_background(self,con,x,y):
        if con == 0:
            col = libtcod.console_get_char_background(0,x,y)
            return libtcod.color_get_hsv(col)
        else:
            col = libtcod.console_get_char_background(self.mConsole[con-1],x,y)
            return libtcod.color_get_hsv(col)
            
    def image_new(self,x,y):
        img = libtcod.image_new(x,y)
        self.mImages.append(img)
        return len(self.mImages)
    
    def image_load(self,path):
        img = libtcod.image_load(path)
        self.mImages.append(img)
        return len(self.mImages)
        
    def image_delete(self,img):
        i = self.mImages.pop(img-1)
        libtcod.image_delete(i)
        
    def image_clear(self,i,r,g,b):
        col = libtcod.Color(r,g,b)
        libtcod.image_clear(self.mImages[i-1],col)
        
    def image_put_pixel(self,i,x,y,r,g,b):
        col = libtcod.Color(r,g,b)
        libtcod.image_put_pixel(self.mImages[i-1],x,y,col)
        
    def image_blit_2x(self,i,c,x,y):
        if c == 0:
            libtcod.image_blit_2x(self.mImages[i-1],0,x,y)
        else:
            libtcod.image_blit_2x(self.mImages[i-1],self.mConsole[c-1],x,y)
        
    def map_init_level(self,sizeX,sizeY):
        self.FOV = libtcod.map_new(sizeX,sizeY)
        #for tile in self.mMap:
        #    tile.explored = False
        
    def map_add_tile(self,x,y,cell,blocked,block_sight,explored,spawn_node):
        self.mMap.append(Tile(x,y,cell,blocked,block_sight,explored,spawn_node))
        
    def map_set_properties(self,x,y,blocked,block_sight):
        libtcod.map_set_properties(self.FOV,x,y,blocked,block_sight)

    def map_clear(self):
        self.mMap = []

    def set_fov_map(self, map):
        self.FOV = map

    def get_fov_map(self):
        return self.FOV

    def get_map(self):
        return self.mMap

    def set_map(self, mMap):
        self.mMap = mMap

    def map_draw(self, con, x, y):
        if con == 0:
            pass
        else:
            con = self.mConsole[con-1]
            libtcod.map_compute_fov(self.FOV,x,y,10,True,libtcod.FOV_RESTRICTIVE)
            for tile in self.mMap:
                if libtcod.map_is_in_fov(self.FOV,tile.x,tile.y):
                    if tile.block_sight:
                        libtcod.console_put_char_ex(con,tile.x,tile.y,tile.cell,self.color_tile_wall,self.color_light_wall)
                    else:
                        libtcod.console_put_char_ex(con,tile.x,tile.y,tile.cell,self.color_tile_ground,self.color_light_ground)
                    tile.explored = True
                else:
                    if tile.explored:
                        if tile.block_sight:
                            libtcod.console_put_char_ex(con,tile.x,tile.y,' ',self.color_tile_wall,self.color_dark_wall)
                        else:
                            libtcod.console_put_char_ex(con,tile.x,tile.y,' ',self.color_tile_ground,self.color_dark_ground)
        
    def map_is_explored(self,x,y):
        for tile in self.mMap:
            if tile.x == x and tile.y == y:
                return tile.explored
        