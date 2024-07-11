############ IMPORTS AND SETTINGS ############

from pathlib import Path
import numpy as np
import glm
from PIL import Image
import moderngl
import moderngl_window as mglw
from moderngl_window.scene import KeyboardCamera
from moderngl_window.scene import Camera
from numba import njit, uint8

CHUNK_SIZE = 32
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE

WORLD_W, WORLD_H = 10, 5
WORLD_D = WORLD_W
WORLD_AREA = WORLD_W * WORLD_H
WORLD_VOL = WORLD_AREA * WORLD_D
WORLD_CENTRE_X = (WORLD_W * CHUNK_SIZE)//2
WORLD_CENTER_Y = (WORLD_H * CHUNK_SIZE)//2
WORLD_CENTER_Z = (WORLD_D * CHUNK_SIZE)//2

MAX_RAY_DIST = 100

glm.silence(2)

############ BASE WINDOW ############

class CameraWindow(mglw.WindowConfig):
    title = "Voxel Cube"
    resource_dir = (Path(__file__).parent / "resources").resolve()
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera.set_position(WORLD_CENTRE_X, WORLD_CENTER_Y, WORLD_CENTER_Z)
        
    def mouse_position_event(self, x: int, y: int, dx, dy):
        self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

############ MESHING ############

@njit
def vertex_to_uint8(x, y, z, voxel_id, face_id, u, v):
    return uint8(x), uint8(y), uint8(z), uint8(voxel_id), uint8(face_id), uint8(u), uint8(v)

@njit
def add_face(vertex_data, index, v0, v1, v2, v3):
    for vertex in (v0, v1, v2, v2, v3, v0):
        for attr in vertex:
            vertex_data[index] = attr
            index += 1
    return index

@njit
def get_chunk_index(world_voxel_pos):
    wx, wy, wz = world_voxel_pos
    cx = wx // CHUNK_SIZE
    cy = wy // CHUNK_SIZE
    cz = wz // CHUNK_SIZE
    if not (0 <= cx < WORLD_W and 0 <= cy < WORLD_H and 0 <= cz < WORLD_D):
        return -1
    return cx + cy * WORLD_W + cz * WORLD_AREA

@njit
def is_empty(local_voxel_pos, world_voxel_pos, world_voxels):
    chunk_index = get_chunk_index(world_voxel_pos)
    if chunk_index == -1:
        return False
    chunk_voxels = world_voxels[chunk_index]
    
    x, y, z = local_voxel_pos
    voxel_index = x % CHUNK_SIZE + y % CHUNK_SIZE * CHUNK_SIZE + z % CHUNK_SIZE * CHUNK_AREA
    if chunk_voxels[voxel_index]:
        return False
    return True

@njit
def construct_chunk_mesh(chunk_voxels, chunk_pos, world_voxels):
    index = 0
    vertex_data = np.empty(CHUNK_VOL * 18 * 7, dtype=np.uint8)
    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                voxel_id = chunk_voxels[x + y * CHUNK_SIZE + z * CHUNK_AREA]
                if voxel_id:
                    cx, cy, cz = chunk_pos
                    wx = x + cx * CHUNK_SIZE
                    wy = y + cy * CHUNK_SIZE
                    wz = z + cz * CHUNK_SIZE

                    if is_empty((x, y + 1, z), (wx, wy + 1, wz), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x + 1 , y + 1 , z + 1, voxel_id, 0, 1, 0),
                        vertex_to_uint8(x + 1, y + 1, z, voxel_id, 0, 1, 1),
                        vertex_to_uint8(x, y + 1, z, voxel_id, 0, 0, 1),
                        vertex_to_uint8(x, y + 1, z + 1, voxel_id, 0, 0, 0))
                    if is_empty((x, y - 1, z), (wx, wy - 1, wz), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x + 1, y, z, voxel_id, 1, 1, 0),
                        vertex_to_uint8(x + 1, y, z + 1, voxel_id, 1, 1, 1),
                        vertex_to_uint8(x, y, z + 1, voxel_id, 1, 0, 1),
                        vertex_to_uint8(x, y, z, voxel_id, 1, 0, 0))
                    if is_empty((x + 1, y, z), (wx + 1, wy, wz), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x + 1, y, z, voxel_id, 2, 1, 0),
                        vertex_to_uint8(x + 1, y + 1 , z, voxel_id, 2, 1, 1),
                        vertex_to_uint8(x + 1, y + 1 , z + 1, voxel_id, 2, 0, 1),
                        vertex_to_uint8(x + 1, y, z + 1, voxel_id, 2, 0, 0))
                    if is_empty((x - 1, y, z), (wx - 1, wy, wz), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x, y, z + 1, voxel_id, 3, 1, 0),
                        vertex_to_uint8(x, y + 1, z + 1, voxel_id, 3, 1, 1),
                        vertex_to_uint8(x, y + 1, z, voxel_id, 3, 0, 1),
                        vertex_to_uint8(x, y, z, voxel_id, 3, 0, 0))
                    if is_empty((x, y, z + 1), (wx, wy, wz + 1), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x + 1, y, z + 1, voxel_id, 4, 1, 0),
                        vertex_to_uint8(x + 1, y + 1 , z + 1, voxel_id, 4, 1, 1),
                        vertex_to_uint8(x, y + 1, z + 1, voxel_id, 4, 0, 1),
                        vertex_to_uint8(x, y, z + 1, voxel_id, 4, 0, 0))   
                    if is_empty((x, y, z - 1), (wx, wy, wz - 1), world_voxels):
                        index = add_face(vertex_data, index, 
                        vertex_to_uint8(x, y, z, voxel_id, 5, 1, 0),
                        vertex_to_uint8(x, y + 1, z, voxel_id, 5, 1, 1),
                        vertex_to_uint8(x + 1 , y + 1 , z, voxel_id, 5, 0, 1),
                        vertex_to_uint8(x + 1, y, z, voxel_id, 5, 0, 0))

    return vertex_data[:index] if index else None

############ VOXEL INTERACTIONS ############

def cast_ray(origin, direction, world_voxels):
    step = glm.sign(direction)
    ray_pos = glm.vec3(origin)
    world_voxel_pos = glm.ivec3(ray_pos)
    t_max = glm.vec3((step - (ray_pos % 1)) / direction)
    t_delta = glm.vec3(step / direction)
    last_axis = -1

    for _ in range(MAX_RAY_DIST):
        chunk_index = get_chunk_index(tuple(world_voxel_pos))
        if chunk_index != -1:
            voxel_index = world_voxel_pos.x % CHUNK_SIZE + (world_voxel_pos.y % CHUNK_SIZE) * CHUNK_SIZE + (world_voxel_pos.z % CHUNK_SIZE) * CHUNK_AREA
            voxel_id = world_voxels[chunk_index][voxel_index]
            if voxel_id:
                normal = glm.vec3(0)
                normal[last_axis] = -step[last_axis]
                return world_voxel_pos, glm.ivec3(normal)
        # Determine which t_max is the smallest, advancing along that axis
        if t_max.x < t_max.y and t_max.x < t_max.z:
            last_axis = 0
            world_voxel_pos.x += step.x
            t_max.x += t_delta.x
        elif t_max.y < t_max.z:
            last_axis = 1
            world_voxel_pos.y += step.y
            t_max.y += t_delta.y
        else:
            last_axis = 2
            world_voxel_pos.z += step.z
            t_max.z += t_delta.z
    return None, None

############ MESH CLASS ############

class ChunkMesh:
    def __init__(self, chunk):
        self.vertex_data = None
        self.index = 0
        self.app = chunk.app
        self.chunk = chunk
        self.ctx = self.app.ctx
        self.program = self.app.program

        self.vbo_format = "3u1 1u1 1u1 2u1"
        self.format_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())
        self.attrs = ("in_position", "voxel_id", "face_id", "in_texcoord")
        self.vao = None

    def build_mesh(self):
        self.vertex_data = construct_chunk_mesh(self.chunk.voxels, self.chunk.position, self.chunk.world.voxels)

    def build_vao(self):
        if self.vertex_data is not None:
            vbo = self.ctx.buffer(self.vertex_data)
            self.vao = self.ctx.vertex_array(
                self.program,
                [(vbo, self.vbo_format, *self.attrs)],
                skip_errors=True
            )

    def render(self):
        if self.vao: self.vao.render()

############ CHUNKS ############

class Chunk:
    def __init__(self, world, position):
        self.app = world.app
        self.world = world
        self.position = position
        self.m_model = glm.translate(glm.mat4(), glm.vec3(self.position) * CHUNK_SIZE)
        self.voxels = None
        self.mesh = ChunkMesh(chunk=self)

    def build_voxels(self):
        voxels = np.zeros(CHUNK_VOL, dtype=np.uint8)

        cx, cy, cz = glm.ivec3(self.position) * CHUNK_SIZE
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                wx = x + cx
                wz = z + cz
                world_height = int(glm.simplex(glm.vec2(wx, wz) * 0.01) * 32 + 32)
                local_height = min(world_height - cy, CHUNK_SIZE)

                for y in range(local_height):
                    voxels[x + y * CHUNK_SIZE + z * CHUNK_AREA] = 6

        return voxels
    
    def render(self):
        self.mesh.program["m_model"].write(self.m_model)
        self.mesh.render()

############ WORLD ############

class World:
    def __init__(self, app):
        self.app = app
        self.chunks = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty((WORLD_VOL, CHUNK_VOL), dtype=np.uint8)
        self.world_voxel_pos_selection, self.normal_selection = None, None
        self.build_chunks()
        self.build_chunk_meshes()

    def build_chunks(self):
        for x in range(WORLD_W):
            for y in range(WORLD_H):
                for z in range(WORLD_D):
                    chunk = Chunk(world=self, position=(x, y, z))
                    chunk_index = x + y * WORLD_W + z * WORLD_AREA
                    self.chunks[chunk_index] = chunk
                    self.voxels[chunk_index] = chunk.build_voxels()
                    chunk.voxels = self.voxels[chunk_index]

    def build_chunk_meshes(self):
        for chunk in self.chunks:
            chunk.mesh.build_mesh()
            chunk.mesh.build_vao()

    def update_chunk(self, chunk_index):
        if chunk_index != -1:
            chunk = self.chunks[chunk_index]
            chunk.mesh.build_mesh()
            chunk.mesh.build_vao()

    def update_voxel_selection(self):
        self.world_voxel_pos_selection, self.normal_selection = cast_ray(origin=glm.vec3(self.app.camera.position), 
                                                                         direction=glm.vec3(glm.cross(self.app.camera.up, self.app.camera.right)), 
                                                                         world_voxels=self.voxels)

    def set_voxel(self):
        if self.world_voxel_pos_selection:
            if self.app.interaction_mode:
                self.add_voxel(self.world_voxel_pos_selection + self.normal_selection)
            else:
                self.remove_voxel(self.world_voxel_pos_selection)
    
    def add_voxel(self, world_voxel_pos):
        chunk_index = get_chunk_index(world_voxel_pos)
        voxel_index = world_voxel_pos.x % CHUNK_SIZE + (world_voxel_pos.y % CHUNK_SIZE) * CHUNK_SIZE + (world_voxel_pos.z % CHUNK_SIZE) * CHUNK_AREA
        new_voxel_id = self.app.voxel_id_selection
        self.voxels[chunk_index][voxel_index] = new_voxel_id
        self.chunks[chunk_index].voxels[voxel_index] = new_voxel_id
        self.update_chunk(chunk_index)

    def remove_voxel(self, world_voxel_pos):
        chunk_index = get_chunk_index(world_voxel_pos)
        wx, wy, wz = world_voxel_pos
        cx, cy, cz = world_voxel_pos % CHUNK_SIZE
        voxel_index = cx + cy * CHUNK_SIZE + cz * CHUNK_AREA
        self.voxels[chunk_index][voxel_index] = 0
        self.chunks[chunk_index].voxels[voxel_index] = 0
        self.update_chunk(chunk_index)
        if cx == 0:
            self.update_chunk(get_chunk_index((wx - 1, wy, wz)))
        elif cx == CHUNK_SIZE - 1:
            self.update_chunk(get_chunk_index((wx + 1, wy, wz)))
        if cy == 0:
            self.update_chunk(get_chunk_index((wx, wy - 1, wz)))
        elif cy == CHUNK_SIZE - 1:
            self.update_chunk(get_chunk_index((wx, wy + 1, wz)))
        if cz == 0:
            self.update_chunk(get_chunk_index((wx, wy, wz - 1)))
        elif cz == CHUNK_SIZE - 1:
            self.update_chunk(get_chunk_index((wx, wy, wz + 1)))

    def render(self):
        for chunk in self.chunks:
            chunk.render()

############ RENDER ###########

class VoxelEngine(CameraWindow):
    title = "Voxel Engine - Tanmay Bansal"
    resource_dir = (Path(__file__).parent / "resources").resolve()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True
        #self.program = self.load_program(path="chunk_simple.glsl")
        self.program = self.load_program(path="chunk_texture_mapped.glsl")
        self.selection_program = self.load_program(path="voxel_selection.glsl")
        self.world = World(self)
        self.ctx.front_face = "ccw"
        self.interaction_mode = 1
        self.voxel_id_selection = 1
        cube_vertices = np.array([
            0, 0, 0,  1, 0, 0,
            1, 0, 0,  1, 1, 0,
            1, 1, 0,  0, 1, 0,
            0, 1, 0,  0, 0, 0,
            0, 0, 1,  1, 0, 1,
            1, 0, 1,  1, 1, 1,
            1, 1, 1,  0, 1, 1,
            0, 1, 1,  0, 0, 1,
            0, 0, 0,  0, 0, 1,
            1, 0, 0,  1, 0, 1,
            1, 1, 0,  1, 1, 1,
            0, 1, 0,  0, 1, 1
        ], dtype=np.float32)
        self.selection_vao = self.ctx.vertex_array(
            self.selection_program,
            [(self.ctx.buffer(cube_vertices), "3f", "in_position")],
            index_buffer=None
        )
        
        self.texture_array = self.load_texture_array("tex_array_0.png", layers=7, flip=True)
        self.texture_array.use(location=0)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        self.camera.key_input(key, action, modifiers)
        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.interaction_mode = (self.interaction_mode + 1) % 2
            elif key == keys.X:
                self.voxel_id_selection = (self.voxel_id_selection) % 7 + 1
            elif key == keys.M:
                self.world.set_voxel()

    def mouse_press_event(self, x, y, button):
        mouse_buttons = self.wnd.mouse
        if button == mouse_buttons.left:
            self.world.set_voxel()

    def render(self, time, frame_time):
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.program["m_proj"].write(self.camera.projection.matrix)
        self.program["m_camera"].write(self.camera.matrix)
        self.world.render()

        self.world.update_voxel_selection()
        if self.world.world_voxel_pos_selection:
            if self.interaction_mode:
                selection_model_matrix = glm.translate(glm.mat4(1.0), glm.vec3(self.world.world_voxel_pos_selection + (self.world.normal_selection) * 1.1))
            else:
                selection_model_matrix = glm.translate(glm.mat4(1.0), glm.vec3(self.world.world_voxel_pos_selection))

            self.selection_program["m_proj"].write(self.camera.projection.matrix)
            self.selection_program["m_camera"].write(self.camera.matrix)
            self.selection_program["m_model"].write(selection_model_matrix)
            self.selection_vao.render(moderngl.LINES)

if __name__ == "__main__":
    mglw.run_window_config(VoxelEngine)