import math

class Vector(object):
#========================================================
    def __init__(self,x=0.0, y=0.0):
#========================================================    
        self.x = x
        self.y = y
        
#========================================================        
    def __str__(self):
#========================================================    
        return "(%s, %s)"%(self.x,self.y)    
    
#========================================================
    @classmethod
    def from_points(cls,P1, P2):
#========================================================
        x1,y1 = P1.x,P1.y
        x2,y2 = P2.x,P2.y
        x = x2 - x1
        y = y2 - y1
        return cls(x,y)
        
#========================================================        
    def get_magnitude(self):
#========================================================    
        return math.sqrt(self.x**2 + self.y**2)

    
#========================================================
    def get_normalized(self):
#========================================================    
        magnitude = self.get_magnitude()
        self.x = self.x / magnitude
        self.y = self.y / magnitude
        return Vector(self.x ,self.y )
        
#========================================================
    def __add__(self,rhs):
#========================================================    
        return Vector(self.x + rhs.x, self.y + rhs.y)
        
#========================================================
    def __sub__(self,rhs):
#========================================================    
        return Vector(self.x - rhs.x, self.y - rhs.y)
        
#========================================================
    def __neg__(self):
#========================================================    
        return Vector(-self.x, -self.y)        
        
#========================================================
    def __mul__(self,scalar):
#========================================================    
        return Vector(self.x * scalar, self.y * scalar)

#========================================================
    def __div__(self,scalar):
#========================================================    
        return Vector(self.x / scalar, self.y / scalar)
        






if __name__ == "__main__":

    A = Vector(10.0,20.0)
    B = Vector(30.0,35.0)
    C = Vector(15.0,45.0)
    AB = Vector.from_points(A,B)
    BC = Vector.from_points(B,C)
    print "Vector AB is", AB
    print "Vector BC is", BC
    print "AB *2 is", AB*2
    print "AB /2 is", AB/2
    print "AB + BC is", AB + BC
    print "AB - BC is", AB - BC
    print "Magnitude of AB is", AB.get_magnitude()
    print "AB Normalized is", AB.get_normalized()
    print "AB Negated is", -AB

    step = AB * .1
    print "AB step is",step

    position = Vector(A[0],A[1])
    print "Looping through steps"
    for n in range(10):
        position += step
        print position
