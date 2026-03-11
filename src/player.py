import math
from my_matrix import Matrix
import entity

WALKING_SPEED = 4.30
SPRINT_SPEED = 6

class Player(entity.Entity):
    def __init__(self, world, shader, width, height):

        super().__init__(world)

        self.v_width = width
        self.v_height = height

        ## matrices

        self.mv_matrix = Matrix()
        self.p_matrix = Matrix()

        ## shader 
        self.shader = shader
        self.shader_matrix_location = self.shader.find_uniform(b"matrix")

        ## camera

        self.eyelevel = self.height - 0.2 
        self.input = [0, 0, 0]

        self.target_speed = WALKING_SPEED
        self.speed = self.target_speed
    
    def update(self, delta_time):
  
        self.speed += (self.target_speed - self.speed) * delta_time * 20

        if self.flying and self.input[1]:
            self.accel[1] = self.input[1] * self.speed

        if self.input[0] or self.input[2]:
            angle = self.rotation[0] - math.atan2(self.input[2], self.input[0]) + math.tau / 4
            
            self.accel[0] = math.cos(angle) * self.speed
            self.accel[2] = math.sin(angle) * self.speed

        if not self.flying and self.input[1] > 0:
            self.jump()
        
        super().update(delta_time)

    def update_matrices(self):
        ## projection matrix

        self.p_matrix.load_identity()
        self.p_matrix.perspective(
            90 + 20 * (self.speed - WALKING_SPEED) / (SPRINT_SPEED - WALKING_SPEED),
            float(self.v_width) / self.v_height, 0.1, 500)

        ## modelview matrix

        self.mv_matrix.load_identity()
        self.mv_matrix.rotate_2d(self.rotation[0] + math.tau / 4, self.rotation[1])
        self.mv_matrix.translate(-self.position[0], -self.position[1] - self.eyelevel, -self.position[2])

        ## modelview projection matrix

        mvp_matrix = self.p_matrix * self.mv_matrix
        self.shader.uniform_matrix(self.shader_matrix_location, mvp_matrix)