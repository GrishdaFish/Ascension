





class Misc:##stairs, chests, other things
    def __init__(self,use_function=None,type=None,game=None):
        self.use_function = use_function
        self.type = type
            
    def use(self):
        self.use_function()
        
