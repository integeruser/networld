import copy
import logging
import threading

import entities as e
import networking as n
import physics as p

logger = logging.getLogger(__name__)

lock = threading.RLock()


class World:
    ADD = 0x1
    DELETE = 0x2
    DIFF = 0x3

    @staticmethod
    def dummy():
        return World()

    @staticmethod
    def diff(from_world, to_world):
        msg = bytearray()
        # update boundaries
        diff = e.Entity.diff(from_world.boundaries, to_world.boundaries)
        n.w_byte(msg, len(diff))
        n.w_blob(msg, diff)

        lock.acquire()
        # update entities
        for entity_id in from_world.entities:
            n.w_byte(msg, entity_id)
            if entity_id in to_world.entities:
                n.w_byte(msg, World.DIFF)
                diff = e.Entity.diff(from_world.entities[entity_id], to_world.entities[entity_id])
                n.w_byte(msg, len(diff))
                n.w_blob(msg, diff)
            else:
                n.w_byte(msg, World.DELETE)
        # add new entities
        for entity_id in to_world.entities:
            if entity_id not in from_world.entities:
                entity = to_world.entities[entity_id]
                n.w_byte(msg, entity_id)
                n.w_byte(msg, World.ADD)
                if isinstance(entity, e.Cube):
                    n.w_byte(msg, e.EntityType.CUBE.value)
                    new = e.Entity.diff(e.Cube.dummy(), entity)
                elif isinstance(entity, e.Sphere):
                    n.w_byte(msg, e.EntityType.SPHERE.value)
                    new = e.Entity.diff(e.Sphere.dummy(), entity)
                else:
                    raise NotImplementedError
                n.w_byte(msg, len(new))
                n.w_blob(msg, new)
        lock.release()
        return msg

    def __init__(self):
        self.boundaries = e.Cube(p.Vector(0, 0, 0), 3)
        self.ids = 0
        self.entities = dict()

        self.paused = False

    def __eq__(self, other):
        return vars(self) == vars(other)

    def _handle_boundaries_collision(self, entity):
        if entity.center.x + entity.size / 2 > self.boundaries.center.x + self.boundaries.size / 2:
            entity.direction.x = -entity.direction.x
        if entity.center.x - entity.size / 2 < self.boundaries.center.x - self.boundaries.size / 2:
            entity.direction.x = -entity.direction.x

        if entity.center.y + entity.size / 2 > self.boundaries.center.y + self.boundaries.size / 2:
            entity.direction.y = -entity.direction.y
        if entity.center.y - entity.size / 2 < self.boundaries.center.y - self.boundaries.size / 2:
            entity.direction.y = -entity.direction.y

        if entity.center.z + entity.size / 2 > self.boundaries.center.z + self.boundaries.size / 2:
            entity.direction.z = -entity.direction.z
        if entity.center.z - entity.size / 2 < self.boundaries.center.z - self.boundaries.size / 2:
            entity.direction.z = -entity.direction.z

    def add_entity(self, entity):
        self.entities[self.ids] = entity
        self.ids += 1

    def draw(self):
        lock.acquire()
        co = copy.deepcopy(self.entities)
        lock.release()
        for entity in co.values():
            entity.draw()
        self.boundaries.draw()

    def toggle_pause(self):
        self.paused = not self.paused

    def tick(self, dt):
        if not self.paused:
            for entity in self.entities.values():
                entity.tick(dt)
            for entity in self.entities.values():
                self._handle_boundaries_collision(entity)

    def update(self, msg):
        logger.info(f'update len(msg)={len(msg)}')

        msg = bytearray(msg)
        # update boundaries
        diff = n.r_blob(msg, n.r_byte(msg))
        self.boundaries.update(diff)
        # update entities
        while msg:
            entity_id = n.r_byte(msg)
            update_type = n.r_byte(msg)
            if update_type == World.ADD:
                entity_type = e.EntityType(n.r_byte(msg))
                new = n.r_blob(msg, n.r_byte(msg))
                self.add_entity(e.Entity.new(entity_type, new))
            elif update_type == World.DELETE:
                del self.entities[entity_id]
            elif update_type == World.DIFF:
                diff = n.r_blob(msg, n.r_byte(msg))
                self.entities[entity_id].update(diff)
            else:
                raise NotImplementedError
        return self


if __name__ == '__main__':
    p.random.seed(1337)

    from_world = World()
    to_world = World()
    to_world.boundaries.color = p.Vector.random()
    colors = [p.Vector(0x00 / 0xFF, 0x99 / 0xFF, 0xCC / 0xFF), p.Vector(0xCC / 0xFF, 0xFF / 0xFF, 0xCC / 0xFF)]
    for i in range(2):
        cube = e.Cube(p.Vector(0, 0, 0), 1)
        cube.speed = p.random.uniform(-3, 3)
        cube.direction = p.Vector.random(-0.5, 0.5).normalize()
        cube.color = colors[i]
        to_world.add_entity(cube)
    colors = [p.Vector(0x66 / 0xFF, 0xCC / 0xFF, 0xFF / 0xFF), p.Vector(0x00 / 0xFF, 0x33 / 0xFF, 0x99 / 0xFF)]
    for i in range(2):
        sphere = e.Sphere(p.Vector(0, 0, 0), p.random.uniform(0.4, 0.8))
        sphere.speed = p.random.uniform(-3, 3)
        sphere.direction = p.Vector.random(-0.5, 0.5).normalize()
        sphere.color = colors[i]
        to_world.add_entity(sphere)
    from_world.update(World.diff(from_world, to_world))
    assert from_world == to_world

    import yaml
    with open('world.yml', 'w') as f:
        yaml.dump(to_world, f)
    with open('world.yml') as f:
        loaded_world = yaml.load(f)
    assert from_world == loaded_world
