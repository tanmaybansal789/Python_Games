from pathlib import Path
import numpy as np
from pyrr import Matrix44
import moderngl
import moderngl_window as mglw
from moderngl_window.scene import KeyboardCamera

CHUNK_SIZE = 32
CHUNK_AREA = CHUNK_SIZE * CHUNK_SIZE
CHUNK_VOL = CHUNK_AREA * CHUNK_SIZE

class CameraWindow(mglw.WindowConfig):
    title = "Voxel Cube"
    resource_dir = (Path(__file__).parent / "resources").resolve()
    aspect_ratio = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        
    def key_event(self, key, action, modifiers):
        self.camera.key_input(key, action, modifiers)

    def mouse_position_event(self, x: int, y: int, dx, dy):
        self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)

class ChunkMesh:
    def __init__(self, chunk, format_data_size=2, vertex_data=None):
        self.vertex_data = vertex_data if vertex_data else np.empty(CHUNK_VOL * 18 * (3 + format_data_size), dtype=np.uint8)
        self.index = 0
        self.app = chunk.app
        self.chunk = chunk
        self.ctx = self.app.ctx
        self.program = self.app.program

        self.vbo_format = "3u1 1u1 1u1"
        self.format_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())
        self.attrs = ("in_position", "voxel_id", "face_id")
        self.vao = None
        
    def add_face(self, v0, v1, v2, v3):
        for vertex in (v0, v1, v2, v2, v3, v0):
            for attr in vertex:
                self.vertex_data[self.index] = attr
                self.index += 1

    def get_raw_vertex_data(self):
        return self.vertex_data[:self.index]

    def get_vao(self):
        vertex_data = self.get_raw_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, self.vbo_format, *self.attrs)],
            skip_errors=True
        )

    def render(self):
        if self.vao: self.vao.render()

class Chunk:
    def __init__(self, app):
        self.app = app
        self.voxels = np.zeros(CHUNK_VOL, dtype=np.uint8)
        self.mesh = ChunkMesh(chunk=self)
        self.build_voxels()
        self.build_mesh()
        self.mesh.get_vao()

    def build_voxels(self):
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    if np.random.randint(2):  self.voxels[x + y * CHUNK_SIZE + z * CHUNK_AREA] = x + y + z + 1

    def is_empty(self, x, y, z):
        if 0 <= x < CHUNK_SIZE and 0 <= y < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            if self.voxels[x + y * CHUNK_SIZE + z * CHUNK_AREA]:
                return False
        return True

    def build_mesh(self):
        self.mesh.index = 0
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    voxel_id = self.voxels[x + y * CHUNK_SIZE + z * CHUNK_AREA]
                    if voxel_id:
                        if self.is_empty(x, y + 1, z):
                            self.mesh.add_face((x + 1 , y + 1 , z + 1, voxel_id, 0),
                            (x + 1, y + 1, z, voxel_id, 0),
                            (x, y + 1, z, voxel_id, 0),
                            (x, y + 1, z + 1, voxel_id, 0))
                        if self.is_empty(x, y - 1, z):
                            self.mesh.add_face((x + 1, y, z, voxel_id, 1),
                            (x + 1, y, z + 1, voxel_id, 1),
                            (x, y, z + 1, voxel_id, 1),
                            (x, y, z, voxel_id, 1))
                        if self.is_empty(x + 1, y, z):
                            self.mesh.add_face((x + 1, y, z, voxel_id, 2),
                            (x + 1, y + 1 , z, voxel_id, 2),
                            (x + 1, y + 1 , z + 1, voxel_id, 2),
                            (x + 1, y, z + 1, voxel_id, 2))
                        if self.is_empty(x - 1, y, z):
                            self.mesh.add_face((x, y, z + 1, voxel_id, 3),
                            (x, y + 1, z + 1, voxel_id, 3),
                            (x, y + 1, z, voxel_id, 3),
                            (x, y, z, voxel_id, 3))
                        if self.is_empty(x, y, z + 1):
                            self.mesh.add_face((x + 1, y, z + 1, voxel_id, 4),
                            (x + 1, y + 1 , z + 1, voxel_id, 4),
                            (x, y + 1, z + 1, voxel_id, 4),
                            (x, y, z + 1, voxel_id, 4))   
                        if self.is_empty(x, y, z - 1):
                            self.mesh.add_face((x, y, z, voxel_id, 5),
                            (x, y + 1, z, voxel_id, 5),
                            (x + 1 , y + 1 , z, voxel_id, 5),
                            (x + 1, y, z, voxel_id, 5))

    def render(self):
        self.mesh.render()

class VoxelEngine(CameraWindow):
    title = "Voxel Cubes"
    resource_dir = (Path(__file__).parent / "resources").resolve()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True
        #self.program = self.load_program(path="chunk_simple.glsl")
        self.program = self.load_program(path="chunk_shading.glsl")
        self.program['m_model'].write(Matrix44.identity(dtype='f4'))
        self.chunk = Chunk(self)
        self.ctx.front_face = "ccw"

        

    def render(self, time, frame_time):
        self.ctx.enable_only(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.program['m_proj'].write(self.camera.projection.matrix)
        self.program['m_camera'].write(self.camera.matrix)
        self.chunk.render()




if __name__ == '__main__':
    mglw.run_window_config(VoxelEngine)
