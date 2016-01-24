import abc

import pyglet

import networking as n
import physics as p


class Entity(metaclass=abc.ABCMeta):
    @staticmethod
    def new(entity):
        msg = bytearray()
        for field in vars(entity):
            value = getattr(entity, field)
            n.w_byte(msg, 0x1)
            if isinstance(value, int):
                n.w_int(msg, value)
            elif isinstance(value, float):
                n.w_float(msg, value)
            elif isinstance(value, p.Vector):
                n.w_vector(msg, value)
            else:
                raise NotImplementedError
        return msg

    @staticmethod
    def diff(from_entity, to_entity):
        msg = bytearray()
        assert len(vars(from_entity)) == len(vars(to_entity))
        for from_field, to_field in zip(vars(from_entity), vars(to_entity)):
            assert type(from_field) == type(to_field)
            from_value = getattr(from_entity, from_field)
            to_value = getattr(to_entity, to_field)

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

    @staticmethod
    def update(entity, msg):
        for field in vars(entity):
            modified = n.r_byte(msg)
            if modified:
                value = vars(entity)[field]
                if isinstance(value, int):
                    setattr(entity, field, n.r_int(msg))
                elif isinstance(value, float):
                    setattr(entity, field, n.r_float(msg))
                elif isinstance(value, p.Vector):
                    setattr(entity, field, n.r_vector(msg))
                else:
                    raise NotImplementedError

    def __init__(self):
        self.id = -1


class Cube(Entity):
    def __init__(self, center, size):
        super().__init__()
        self.center = center
        self.size = size
        self.orientation = p.Vector(0, 0, 0)
        self.speed = 0
        self.direction = p.Vector(0, 0, 0)
        self.color = p.Vector.random(0, 1)

    def __str__(self):
        return 'Cube: [%s, %f]' % (self.center, self.size)

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

    def update(self, dt):
        self.center.move(dt * self.speed, self.direction)


if __name__ == '__main__':

    def test01():
        from_entity = Cube(p.Vector(1, 2, 3), 1337)
        to_entity = Cube(p.Vector(4, 5, 6), 42)
        Entity.update(from_entity, Entity.diff(from_entity, to_entity))
        assert from_entity.center == to_entity.center and from_entity.size == to_entity.size

    test01()
    print('All tests passed!')
