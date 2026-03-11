import math
import collider

FLY_ACCEL = (0, 0, 0)
GRAVITY_ACCEL = (0, -32, 0)

FRICTION = (20, 20, 20)
FLY_DRAG = (5, 5, 5)
JUMP_DRAG = (1.9, 0, 1.9)
FALL_DRAG = (1.9, 0.4, 1.9)

class Entity:
    def __init__(self, world):

        self.world = world

        self.jump_height = 1.25
        self.flying = False

        self.position = [0, 5, 0]
        self.rotation = [-math.tau / 4, 0]

        self.velocity = [0, 0, 0]
        self.accel = [0, 0, 0]

        self.width = 0.6
        self.height = 1.8

        self.collider = collider.Collider()
        self.on_ground = False

    def update_collider(self):
        x, y, z = self.position


        self.collider.x1 = x - self.width / 2
        self.collider.x2 = x + self.width / 2

        self.collider.y1 = y 
        self.collider.y2 = y + self.height

        self.collider.z1 = z - self.width / 2
        self.collider.z2 = z + self.width / 2

    def jump(self, height = None):
        if not self.on_ground:
            return
        
        if height is None:
            height = self.jump_height
        self.velocity[1] = math.sqrt(-2 * GRAVITY_ACCEL[1] * height)

    @property
    def friction(self):
        if self.flying:
            return FLY_DRAG
        elif self.on_ground:
            return FRICTION
        elif self.velocity[1] > 0:
            return JUMP_DRAG
        
        return FALL_DRAG

    def update(self, delta_time):

        self.velocity = [v + a * f * delta_time for v, a, f in zip(self.velocity, self.accel, self.friction)]
        self.accel = [0, 0, 0]

        self.update_collider()
        self.on_ground = False

        for _ in range(3):
            a_vel = [v * delta_time for v in self.velocity]
            vx, vy, vz = a_vel

            step_x = 1 if vx > 0 else -1
            step_y = 1 if vy > 0 else -1
            step_z = 1 if vz > 0 else -1

            steps_xz = int(self.width / 2)
            steps_y = int(self.height)

            x, y, z = map(int, self.position)
            current_x, current_y, current_z = [int(x + v) for x, v in zip(self.position, a_vel)]

            potentional_col = []

            for i in range(x - step_x * (steps_xz + 1), current_x + step_x * (steps_xz + 2), step_x):
                for j in range(y - step_y * (steps_xz + 2), current_y + step_y * (steps_xz + 3), step_y):
                    for k in range(z - step_z * (steps_xz + 1), current_z + step_z * (steps_xz + 2), step_z):
                        pos = (i, j, k)
                        num = self.world.get_block_number(pos)

                        if not num: continue

                        for _c in self.world.block_types[num].colliders:
                            entry_time, normal = self.collider.collide(_c + pos, a_vel)

                            if normal is None: continue

                            potentional_col.append((entry_time, normal))

            if not potentional_col:
                break
            entry_time, normal = min(potentional_col, key = lambda x: x[0])
            entry_time -= 0.001
            
            if normal[0]:
                self.velocity[0] = 0
                self.position[0] += vx * entry_time
                
            if normal[1]:
                self.velocity[1] = 0
                self.position[1] += vy * entry_time

            if normal[2]:
                self.velocity[2] = 0
                self.position[2] += vz * entry_time

            if normal[1] == 1:
                self.on_ground = True

        self.position = [x + v * delta_time for x, v in zip(self.position, self.velocity)]

        gravity = FLY_ACCEL if self.flying else GRAVITY_ACCEL
        self.velocity = [v + a * delta_time for v, a in zip(self.velocity, gravity)]

        self.velocity = [v - min(v * f * delta_time, v, key = abs)for v, f in zip(self.velocity, self.friction)]

        self.update_collider()
