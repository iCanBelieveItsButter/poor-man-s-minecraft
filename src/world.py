import chunk

import block_type
import texture_manager

import math
import random

class World:
    def __init__(self):
        self.texture_manager = texture_manager.Texture_manager(16, 16, 256)
        self.block_types = [None]

        self.block_types.append(block_type.Block_type(self.texture_manager, "cobble", {"all": "cobble"}))
        self.block_types.append(block_type.Block_type(self.texture_manager, "dirt", {"all": "dirt"}))
       ## self.block_types.append(block_type.Block_type(self.texture_manager, "grass", {"top": "grass", "bottom": "dirt", "sides": "grass_side"}))

        self.texture_manager.generate_mipmaps()

        self.chunks = {}
        self.chunks[(0, 0, 0)] = chunk.Chunk(self, (0, 0, 0))

        for x in range(8):
            for z in range(8):
                chunk_position = (x - 4, -1, z - 4)
                current_chunk = chunk.Chunk(self, chunk_position)

                for i in range(chunk.CHUNK_W):
                    for j in range(chunk.CHUNK_H):
                        for k in range(chunk.CHUNK_L):
                            if j > 13:
                                current_chunk.blocks[i][j][k] = random.choice([0, 2])
                            else:
                                current_chunk.blocks[i][j][k] = random.choice([0, 0, 1])

                self.chunks[chunk_position] = current_chunk

        for chunk_position in self.chunks:
            self.chunks[chunk_position].update_mesh()

    def get_block_number(self, pos):
        x, y, z = pos

        chunk_position = (
            math.floor(x / chunk.CHUNK_W),
            math.floor(y / chunk.CHUNK_H),
            math.floor(z / chunk.CHUNK_L))
        
        if not chunk_position in self.chunks:
            return 0 ## air

        local_X = int(x % chunk.CHUNK_W)
        local_Y = int(y % chunk.CHUNK_H)
        local_Z = int(z % chunk.CHUNK_L)

        return self.chunks[chunk_position].blocks[local_X][local_Y][local_Z]

    def draw(self):
        for chunk_position in self.chunks:
            self.chunks[chunk_position].draw()