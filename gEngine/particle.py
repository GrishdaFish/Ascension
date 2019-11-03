__author__ = 'Grishnak'
import math
import libtcodpy as libtcod


def explosion(num_particles, particle_array, x, y, random_decay=True, bounce=True, color=None):
    for i in range(num_particles):
        particle_array.append(Particle(x, y, 0.15, 1.0, random_decay=random_decay, bounce=bounce, color=None))


def nova(num_particles, particle_array, x, y, random_decay=False, bounce=False):
    increment = (num_particles) / 3.14159
    angle = math.atan2(float(-y), float(-x))
    for i in range(num_particles/2):
        angle = i+increment
        particle_array.append(Particle(x,y,0.1,1.0,angle, random_decay, bounce))
    for i in range(num_particles/2):
        angle = i-increment
        particle_array.append(Particle(x,y,0.1,1.0,-angle, random_decay, bounce))


def cone_spray(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    for i in range(num_particles):
        angle2 = angle + libtcod.random_get_float(0, -0.25, 0.25)
        velocity = 1.0 + libtcod.random_get_float(0, -0.05, 0.05)
        decay = 0.09 + libtcod.random_get_float(0, -0.05, 0.05)
        particle_array.append(Particle(ox,oy,decay,velocity, angle2, random_decay, bounce))


def cone(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    for i in range(num_particles):
        angle2 = angle + libtcod.random_get_float(0, -0.25, 0.25)
        velocity = 1.0
        decay = 0.1
        particle_array.append(Particle(ox,oy,decay,velocity, angle2, random_decay, bounce))


def projectile(num_particles, particle_array, ox, oy, dx, dy, random_decay=False, bounce=False):
    ay = oy - dy
    ax = ox - dx
    angle = math.atan2(float(-ay), float(-ax))
    particle_array.append(Particle(ox, oy, 0.05, 1.0, angle, random_decay, bounce))


def uniform_intensity_burst(color):
    factor = 3.0
    clamp = 1.5
    #generate a random number with a combined light intensity of 3.0 (brighter than any standard light)
    if not color:
        r = libtcod.random_get_float(0, 0.1, 1.5)
        g = libtcod.random_get_float(0, 0.1, 1.5)
        b = libtcod.random_get_float(0, 0.1, 1.5)
    else:
        r = color[0]/255
        g = color[1]/255
        b = color[2]/255

    #add them all together, then divide them by our target intensity
    s = r+g+b
    f = factor / s

    #then multiply the originally generated numbers by the factor to get target intensity
    r = min(clamp, r*f) #but clamp to 1.5 intensity to prevent washout of a single color being too bright
    g = min(clamp, g*f)
    b = min(clamp, b*f)

    #get sum again (to maintain overall intensity, likely isnt completely accurate,
    #but it is close enough to the intention
    s = r+g+b
    f = factor / s
    if s < factor:
        if r == clamp:
            g = g*f
            b = b*f
        elif g == clamp:
            r = r*f
            b = b*f
        else:
            r = r*f
            g = g*f

    return (r, g, b)


class Particle:
    def __init__(self, x, y, decay=0.1, velocity=1.0, angle=None, random_decay=True, bounce=False, color=None):
        self.x = x
        self.y = y
        self.decay = decay
        self.can_bounce = bounce

        if random_decay:
            self.decay += libtcod.random_get_float(0, -0.05, 0.05)
        self.velocity = velocity
        self.dead = False
        if angle == None:
            self.angle = math.atan2(float(-y), float(-x))
            self.angle += libtcod.random_get_float(0, -3.14159, 3.14159)
        else:
            self.angle = angle
        self.dir_x = math.cos(self.angle * self.velocity)
        self.dir_y = math.sin(self.angle * self.velocity)
        self.color = uniform_intensity_burst(color)

    def update(self, lightmask=None, map=None):
        if self.dead:
            return

        newx = self.x + self.dir_x * self.velocity
        newy = self.y + self.dir_y * self.velocity

        if self.velocity <= 0:
            self.dead = True
            return

        if map:
            collide = map[int(newx)][int(newy)].blocked
            if collide:
                if self.can_bounce:
                    #determine angle of bounce with black magic
                    cdx = int(newx - self.x) / 2
                    cdy = int(newy - self.y) / 2

                    if cdx == 0:
                        self.dir_y = (-self.dir_y)
                    if cdy == 0:
                        self.dir_x = (-self.dir_y)
                    else:
                        self.dead = True
                    #    return
                else:
                    self.dead = True
                    return

            self.x = newx
            self.y = newy
            self.velocity -= self.decay

            if lightmask:
                lightmask.add_light(int(self.x), int(self.y), self.color)

    def draw(self, gEngine):  # change this to lightmap drawing once subcell res is implemented
        gEngine.console_put_char_ex(0, int(self.x), int(self.y), " ", 255, 255, 255, 0, 0, 0)

    def get_angle(self, dx, dy):
        self.angle = math.atan2(float(dy), float(dx))
        return self.angle