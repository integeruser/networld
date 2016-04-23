import abc
import enum

import pyglet

import networking as n
import physics as p


class Entity(metaclass=abc.ABCMeta):
    @staticmethod
    def new(entity_type, msg):
        if entity_type == EntityType.CUBE:
            return Cube.dummy().update(msg)
        elif entity_type == EntityType.SPHERE:
            return Sphere.dummy().update(msg)
        else:
            raise NotImplementedError

    @staticmethod
    def diff(from_entity, to_entity):
        msg = bytearray()
        for var in vars(from_entity):
            from_value = getattr(from_entity, var)
            to_value = getattr(to_entity, var)
            if from_value == to_value:
                n.w_byte(msg, 0x0)
            else:
                n.w_byte(msg, 0x1)
                if isinstance(from_value, int):
                    n.w_int(msg, to_value)
                elif isinstance(from_value, float):
                    n.w_float(msg, to_value)
                elif isinstance(from_value, p.Vector):
                    n.w_vector(msg, to_value)
                else:
                    raise NotImplementedError
        return msg

    def __eq__(self, other):
        return vars(self) == vars(other)

    def update(self, msg):
        for var in vars(self):
            updated = n.r_byte(msg)
            if updated:
                value = vars(self)[var]
                if isinstance(value, int):
                    setattr(self, var, n.r_int(msg))
                elif isinstance(value, float):
                    setattr(self, var, n.r_float(msg))
                elif isinstance(value, p.Vector):
                    setattr(self, var, n.r_vector(msg))
                else:
                    raise NotImplementedError
        return self


class Cube(Entity):
    @staticmethod
    def dummy():
        return Cube(p.Vector(1337, 1338, 1339), 13310)

    def __init__(self, center, size):
        super().__init__()
        self.center = center
        self.size = size
        self.orientation = p.Vector(0, 0, 0)
        self.speed = 0
        self.direction = p.Vector(0, 0, 0)
        self.color = p.Vector(1, 1, 1)

    def draw(self):
        pyglet.gl.glPushMatrix()

        pyglet.gl.glTranslatef(self.center.x, self.center.y, self.center.z)
        pyglet.gl.glRotatef(self.orientation.x, 1, 0, 0)
        pyglet.gl.glRotatef(self.orientation.y, 0, 1, 0)
        pyglet.gl.glRotatef(self.orientation.z, 0, 0, 1)

        pyglet.gl.glColor3f(self.color.x, self.color.y, self.color.z)

        pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_LINE)
        pyglet.gl.glBegin(pyglet.gl.GL_QUADS)
        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, self.size / 2)

        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, -self.size / 2)

        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, -self.size / 2)

        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, -self.size / 2)

        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, self.size / 2, -self.size / 2)

        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, self.size / 2)
        pyglet.gl.glVertex3f(-self.size / 2, -self.size / 2, -self.size / 2)
        pyglet.gl.glVertex3f(self.size / 2, -self.size / 2, -self.size / 2)
        pyglet.gl.glEnd()
        pyglet.gl.glPolygonMode(pyglet.gl.GL_FRONT_AND_BACK, pyglet.gl.GL_FILL)

        pyglet.gl.glPopMatrix()

    def tick(self, dt):
        self.center.move(dt * self.speed, self.direction)


class Sphere(Entity):
    @staticmethod
    def dummy():
        return Sphere(p.Vector(1337, 1338, 1339), 13310)

    def __init__(self, center, radius):
        super().__init__()
        self.center = center
        self.size = radius
        self.speed = 0
        self.direction = p.Vector(0, 0, 0)
        self.color = p.Vector(1, 1, 1)

    def draw(self):
        pyglet.gl.glPushMatrix()

        pyglet.gl.glTranslatef(self.center.x, self.center.y, self.center.z)

        pyglet.gl.glColor3f(self.color.x, self.color.y, self.color.z)

        raise NotImplementedError

        pyglet.gl.glPopMatrix()

    def tick(self, dt):
        self.center.move(dt * self.speed, self.direction)


class EntityType(enum.Enum):
    CUBE = 0x1
    SPHERE = 0x2


if __name__ == '__main__':
    to_entity = Cube(p.Vector(4, 5, 6), 42)
    assert Entity.new(EntityType.CUBE, Entity.diff(Cube.dummy(), to_entity)) == to_entity

    to_entity = Sphere(p.Vector(4, 5, 6), 42)
    assert Entity.new(EntityType.SPHERE, Entity.diff(Sphere.dummy(), to_entity)) == to_entity

    from_entity = Cube(p.Vector(1, 2, 3), 1337)
    to_entity = Cube(p.Vector(4, 5, 6), 42)
    to_entity.orientation = p.Vector.random()
    to_entity.direction = p.Vector.random()
    to_entity.color = p.Vector.random()
    from_entity.update(Entity.diff(from_entity, to_entity))
    assert from_entity == to_entity

    from_entity = Sphere(p.Vector(1, 2, 3), 1337)
    to_entity = Sphere(p.Vector(4, 5, 6), 42)
    to_entity.direction = p.Vector.random()
    to_entity.color = p.Vector.random()
    from_entity.update(Entity.diff(from_entity, to_entity))
    assert from_entity == to_entity

    assert Cube(p.Vector(1, 2, 3), 1337) != Sphere(p.Vector(1, 2, 3), 1337)

    print('All tests passed!')
