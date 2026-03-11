import chunk

import block_type
import texture_manager

import math
import random

import models.plant

class World:
    def __init__(self):
        self.texture_manager = texture_manager.Texture_manager(16, 16, 256)
        self.block_types = [None]

        self.block_types.append(block_type.Block_type(self.texture_manager, "cobble", {"all": "cobble"}))
        self.block_types.append(block_type.Block_type(self.texture_manager, "grass", {"all": "grass"}))
        self.block_types.append(block_type.Block_type(self.texture_manager, "flower", {"all": "flower"}, models.plant))
        self.block_types.append(block_type.Block_type(self.texture_manager, "dirt", {"all": "dirt"}))

        self.texture_manager.generate_mipmaps()

        self.chunks = {}
        self.chunks[(0, 0, 0)] = chunk.Chunk(self, (0, 0, 0))

        for x in range(8):
            for z in range(8):
                chunk_position = (x - 4, -1, z - 4)
                current_chunk = chunk.Chunk(self, chunk_position)

                for i in range(chunk.CHUNK_WIDTH):
                    for j in range(chunk.CHUNK_HEIGHT):
                        for k in range(chunk.CHUNK_LENGTH):
                            if j == 15:
                                if current_chunk.blocks[i][j-1][k] == 2:
                                    current_chunk.blocks[i][j][k] = random.choice([0, 0, 3])
                            elif j > 13:
                                current_chunk.blocks[i][j][k] = 2
                            else:
                                current_chunk.blocks[i][j][k] = random.choice([0, 0, 1])

                self.chunks[chunk_position] = current_chunk

        for chunk_position in self.chunks:
            self.chunks[chunk_position].update_subchunk_meshes()
            self.chunks[chunk_position].update_mesh()



    def get_chunk_position(self, pos):
        x, y, z = pos

        return (
            math.floor(x / chunk.CHUNK_WIDTH),
            math.floor(y / chunk.CHUNK_HEIGHT),
            math.floor(z / chunk.CHUNK_LENGTH)
        )

    def get_local_position(self, pos):
        x, y, z = pos

        return (
            int(x % chunk.CHUNK_WIDTH),
            int(y % chunk.CHUNK_HEIGHT),
            int(z % chunk.CHUNK_LENGTH)
        )



    def get_block_number(self, pos):
        x, y, z = pos
        
        chunk_pos = self.get_chunk_position(pos)

        if not chunk_pos in self.chunks:
            return 0
        
        lx, ly, lz = self.get_local_position(pos)

        block_number = self.chunks[chunk_pos].blocks[lx][ly][lz]
        return block_number

    def is_opaque_block(self, pos):
       block_type = self.block_types[self.get_block_number(pos)]

       if not block_type:
           return False
       
       return not block_type.transparent

    def set_block(self, pos, number):
        x, y, z = pos
        chunk_pos = self.get_chunk_position(pos)

        if not chunk_pos in self.chunks:
            if number == 0:
                return
        
            self.chunks[chunk_pos] = chunk.Chunk(self, chunk_pos)

        ## if existing block is different than the one we are "setting"
        if self.get_block_number(pos) == number:
            return
        
        lx, ly, lz = self.get_local_position(pos)

        self.chunks[chunk_pos].blocks[lx][ly][lz] = number
        self.chunks[chunk_pos].update_at_position((x, y, z))
        self.chunks[chunk_pos].update_mesh()

        cx, cy, cz = chunk_pos

        def try_update_chunk_at_position(chunk_pos, position):
            if chunk_pos in self.chunks:
                self.chunks[chunk_pos].update_at_position(position)
                self.chunks[chunk_pos].update_mesh()
        
        if lx == chunk.CHUNK_WIDTH - 1: try_update_chunk_at_position((cx + 1, cy, cz), (x + 1, y, z))
        if lx == 0: try_update_chunk_at_position((cx - 1, cy, cz), (x - 1, y, z))

        if ly == chunk.CHUNK_HEIGHT - 1: try_update_chunk_at_position((cx, cy + 1, cz), (x, y + 1, z))
        if ly == 0: try_update_chunk_at_position((cx, cy - 1, cz), (x, y - 1, z))

        if lz == chunk.CHUNK_LENGTH - 1: try_update_chunk_at_position((cx, cy, cz + 1), (x, y, z + 1))
        if lz == 0: try_update_chunk_at_position((cx, cy, cz - 1), (x, y, z - 1))

    def try_set_block(self, pos, num, collider):
        if not num:
            return self.set_block(pos, 0)
        
        for block_col in self.block_types[num].colliders:
            if collider & (block_col + pos):
                return
            
        self.set_block(pos, num)

    def draw(self):
        for chunk_position in self.chunks:
            self.chunks[chunk_position].draw()