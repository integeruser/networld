import abc

import networking as n
import physics as p


class Entity(metaclass=abc.ABCMeta):
    @staticmethod
    def diff(from_ent, to_ent):
        msg = bytearray()

        if to_ent:
            assert len(vars(from_ent)) == len(vars(to_ent))
            for from_field, to_field in zip(vars(from_ent), vars(to_ent)):
                assert type(from_field) == type(to_field)
                from_value = getattr(from_ent, from_field)
                to_value = getattr(to_ent, to_field)

                if from_value == to_value:
                    n.w_byte(msg, 0)
                else:
                    n.w_byte(msg, 1)
                    if isinstance(from_value, int):
                        n.w_int(msg, to_value)
                    elif isinstance(from_value, float):
                        n.w_float(msg, to_value)
                    elif isinstance(from_value, p.Vector):
                        n.w_vector(msg, to_value)
                    else:
                        raise NotImplementedError
        else:
            # the entity has been deleted
            raise NotImplementedError
        return msg

    @staticmethod
    def update(ent, msg):
        for field in vars(ent):
            modified = n.r_byte(msg)
            if modified:
                value = vars(ent)[field]
                if isinstance(value, int):
                    setattr(ent, field, n.r_int(msg))
                elif isinstance(value, float):
                    setattr(ent, field, n.r_float(msg))
                elif isinstance(value, p.Vector):
                    setattr(ent, field, n.r_vector(msg))
                else:
                    raise NotImplementedError


class Cube(Entity):
    def __init__(self, center, size):
        self.center = center
        self.size = size
        self.orientation = p.Vector(0, 0, 0)
        self.speed = 0
        self.direction = p.Vector(0, 0, 0)
        self.color = p.Vector.random(0, 1)

    def __str__(self):
        return 'Cube: [%s, %f]' % (self.center, self.size)

    def update(self, dt):
        self.center.move(dt*self.speed, self.direction)


if __name__ == '__main__':
    def test01():
        from_ent = Cube(p.Vector(1, 2, 3), 1337)
        to_ent = Cube(p.Vector(4, 5, 6), 42)
        Entity.update(from_ent, Entity.diff(from_ent, to_ent))
        assert from_ent.center == to_ent.center and from_ent.size == to_ent.size

    test01()
    print('All tests passed!')
