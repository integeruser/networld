import itertools
import random

import entities as e
import networking as n
import physics as p


class World:
    ADD = 0x1
    DELETE = 0x2
    DIFF = 0x3

    @staticmethod
    def diff(from_world, to_world):
        msg = bytearray()
        # update old entities
        for entity_id in from_world.entities:
            if entity_id in to_world.entities:
                from_entity = from_world.entities[entity_id]
                to_entity = to_world.entities[entity_id]
                n.w_byte(msg, from_entity.id)
                n.w_byte(msg, World.DIFF)
                msg.extend(e.Entity.diff(from_entity, to_entity))
                n.w_byte(msg, 0xF)
            else:
                n.w_byte(msg, entity.id)
                n.w_byte(msg, World.DELETE)
                n.w_byte(msg, 0xF)
        # add new entities
        for entity_id in to_world.entities:
            if entity_id not in from_world.entities:
                entity = to_world.entities[entity_id]
                n.w_byte(msg, entity.id)
                n.w_byte(msg, World.ADD)
                msg.extend(e.Entity.new(entity))
                n.w_byte(msg, 0xF)
        return msg

    @staticmethod
    def dummy():
        w = World()
        w.entities = list()
        return w

    @staticmethod
    def update(world, l, msg):
        for _ in range(l):
            entity_id = n.r_byte(msg)
            status = n.r_byte(msg)
            if status == World.ADD:
                pass
            elif status == World.DELETE:
                pass
            elif status == World.DIFF:
                pass
            else:
                raise NotImplementedError

    def __init__(self):
        self.boundaries = e.Cube(p.Vector(0, 0, 0), 3)
        self.boundaries.color = p.Vector(1, 1, 1)
        self.entity_count = itertools.count()
        self.entities = dict()
        for i in range(random.randint(3, 6)):
            self.add_entity(e.Cube(p.Vector.random(), i))

    def _handle_boundaries_collision(self, entity):
        if entity.direction.x > 0:
            if entity.center.x + entity.size / 2 > self.boundaries.center.x + self.boundaries.size / 2:
                entity.direction.x = -entity.direction.x
        else:
            if entity.center.x - entity.size / 2 < self.boundaries.center.x - self.boundaries.size / 2:
                entity.direction.x = -entity.direction.x

        if entity.direction.y > 0:
            if entity.center.y + entity.size / 2 > self.boundaries.center.y + self.boundaries.size / 2:
                entity.direction.y = -entity.direction.y
        else:
            if entity.center.y - entity.size / 2 < self.boundaries.center.y - self.boundaries.size / 2:
                entity.direction.y = -entity.direction.y

        if entity.direction.z > 0:
            if entity.center.z + entity.size / 2 > self.boundaries.center.z + self.boundaries.size / 2:
                entity.direction.z = -entity.direction.z
        else:
            if entity.center.z - entity.size / 2 < self.boundaries.center.z - self.boundaries.size / 2:
                entity.direction.z = -entity.direction.z

    def add_entity(self, entity):
        entity_id = next(self.entity_count)
        self.entities[entity_id] = entity

    def delete_entity(self, entity_id):
        del self.entities[entity_id]

    def draw(self):
        self.boundaries.draw()
        for entity in self.entities.values():
            entity.draw()

    def update(self, dt):
        for entity in self.entities.values():
            entity.update(dt)
        for entity in self.entities.values():
            self._handle_boundaries_collision(entity)


if __name__ == '__main__':

    def test01():
        from_world = World()
        to_entity = World()
        Entity.update(from_entity, Entity.diff(from_entity, to_entity))
        assert from_entity.center == to_entity.center and from_entity.size == to_entity.size

    test01()
    print('All tests passed!')
