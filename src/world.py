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
        # update boundaries
        diff = e.Entity.diff(from_world.boundaries, to_world.boundaries)
        n.w_byte(msg, len(diff))
        n.w_blob(msg, diff)
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
        return msg

    def __init__(self):
        self.boundaries = e.Cube(p.Vector(0, 0, 0), 3)
        self.ids = 0
        self.entities = dict()

    def __eq__(self, other):
        return vars(self) == vars(other)

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
        self.entities[self.ids] = entity
        self.ids += 1

    def draw(self):
        self.boundaries.draw()
        for entity in self.entities.values():
            entity.draw()

    def tick(self, dt):
        for entity in self.entities.values():
            entity.tick(dt)
        for entity in self.entities.values():
            self._handle_boundaries_collision(entity)

    def update(self, msg):
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
    from_world = World()
    to_world = World()
    to_world.boundaries.color = p.Vector.random()
    for _ in range(p.random.randint(1, 5)):
        if p.random.random() < 0.5:
            cube = e.Cube(p.Vector(0, 0, 0), p.random.randint(4, 19))
            cube.speed = p.random.randint(3, 10)
            cube.direction = p.Vector.random(-100, 100).normalize()
            to_world.add_entity(cube)
        else:
            sphere = e.Sphere(p.Vector(0, 0, 0), p.random.randint(4, 19))
            sphere.speed = p.random.randint(3, 10)
            sphere.direction = p.Vector.random(-100, 100).normalize()
            to_world.add_entity(sphere)
    from_world.update(World.diff(from_world, to_world))
    assert from_world == to_world

    print('All tests passed!')
