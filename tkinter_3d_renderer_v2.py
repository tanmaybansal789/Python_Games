import tkinter as tk
from tkinter import ttk, simpledialog
from math import sin, cos, radians, sqrt
from stl import mesh
import tkinter.filedialog as filedialog


SHAPES = {
    'octahedron': {
        'vertices': [
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1)
        ],
        'faces': [
            [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
            [0, 5, 2], [2, 5, 1], [1, 5, 3], [3, 5, 0]
        ]
    },
    'tetrahedron': {
        'vertices': [
            (0, 1, 0),
            ((8/9)**0.5, -1/3, 0),
            (-(2/9)**0.5, -1/3, (2/3)**0.5),
            (-(2/9)**0.5, -1/3, -(2/3)**0.5)
        ],
        'faces': [
            [2, 1, 0],
            [3, 2, 0],
            [1, 3, 0],
            [1, 2, 3]
    ]},

    'cylinder': {
        'vertices': [
            (1.0, 0.0, 1.0),
            (1.0, 0.0, -1.0),
            (0.87, 0.5, 1.0),
            (0.87, 0.5, -1.0),
            (0.5, 0.87, 1.0),
            (0.5, 0.87, -1.0),
            (0.0, 1.0, 1.0),
            (0.0, 1.0, -1.0),
            (-0.5, 0.87, 1.0),
            (-0.5, 0.87, -1.0), 
            (-0.87, 0.5, 1.0),
            (-0.87, 0.5, -1.0),
            (-1.0, 0.0, 1.0),
            (-1.0, 0.0, -1.0),
            (-0.87, -0.5, 1.0),
            (-0.87, -0.5, -1.0),
            (-0.5, -0.87, 1.0),
            (-0.5, -0.87, -1.0),
            (0.0, -1.0, 1.0),
            (0.0, -1.0, -1.0),
            (0.5, -0.87, 1.0),
            (0.5, -0.87, -1.0),
            (0.87, -0.5, 1.0),
            (0.87, -0.5, -1.0)],
        'faces': [
            [0, 1, 2],
            [2, 1, 3],
            [2, 3, 4],
            [4, 3, 5],
            [4, 5, 6],
            [6, 5, 7],
            [6, 7, 8],
            [8, 7, 9],
            [8, 9, 10],
            [10, 9, 11],
            [10, 11, 12],
            [12, 11, 13],
            [12, 13, 14],
            [14, 13, 15],
            [14, 15, 16],
            [16, 15, 17],
            [16, 17, 18],
            [18, 17, 19],
            [18, 19, 20],
            [20, 19, 21],
            [20, 21, 22],
            [22, 21, 23],
            [22, 23, 0],
            [0, 23, 1],
            [23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1],
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]]},
    'icosahedron': {
        'vertices': [
            (-1, 1.6180339887, 0), (1, 1.6180339887, 0), (-1, -1.6180339887, 0), (1, -1.6180339887, 0),
            (0, -1, 1.6180339887), (0, 1, 1.6180339887), (0, -1, -1.6180339887), (0, 1, -1.6180339887),
            (1.6180339887, 0, -1), (1.6180339887, 0, 1), (-1.6180339887, 0, -1), (-1.6180339887, 0, 1)
        ],
        'faces': [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]
        ]},
    'cube': {
        'vertices': [
            (-1, -1, -1),
            (-1, -1, 1),   
            (-1, 1, -1),   
            (-1, 1, 1),    
            (1, -1, -1),   
            (1, -1, 1),    
            (1, 1, -1),    
            (1, 1, 1),    
      ],
      'faces': [
              [2, 6, 4, 0],  # Back face
              [5, 7, 3, 1],  # Front face
              [4, 5, 1, 0],  # Bottom face
              [3, 7, 6, 2],  # Top face
              [1, 3, 2, 0],  # Left face
              [6, 7, 5, 4],  # Right face
        ]}       
}

def normalize(vector):
    mag = sqrt(sum(pow(element, 2) for element in vector))
    return tuple(element / (mag + 0.01) for element in vector)

def vector_subtract(a, b):
    return tuple(ai - bi for ai, bi in zip(a, b))

def dot_product(a, b):
    return sum(ai * bi for ai, bi in zip(a, b))

def cross_product(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def rotate_x(angle, vertices):
    rad = radians(angle)
    cos_angle, sin_angle = cos(rad), sin(rad)
    return [(x, y * cos_angle - z * sin_angle, y * sin_angle + z * cos_angle) for x, y, z in vertices]

def rotate_y(angle, vertices):
    rad = radians(angle)
    cos_angle, sin_angle = cos(rad), sin(rad)
    return [(x * cos_angle + z * sin_angle, y, -x * sin_angle + z * cos_angle) for x, y, z in vertices]

def rotate_z(angle, vertices):
    rad = radians(angle)
    cos_angle, sin_angle = cos(rad), sin(rad)
    return [(x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle, z) for x, y, z in vertices]

def translate(vertices, offset):
    ox, oy, oz = offset
    return [(x + ox, y + oy, z + oz) for x, y, z in vertices]

def reshape(vertices, scale):
    sx, sy, sz = scale
    return [(x * sx, y * sy, z * sz) for x, y, z in vertices]

class Object3D:
    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces


class AddEntryDialog(simpledialog.Dialog):
    def __init__(self, master, type_necessary=True):
        self.type_necessary = type_necessary
        super().__init__(master)

    def body(self, master):
        self.title('Add New Entry')
        
        labels = ['pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z', 'scale_x', 'scale_y', 'scale_z']
        if self.type_necessary: labels.insert(0, "Type")
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(master, text=label).grid(row=i, column=0)
            self.entries[label] = tk.Entry(master)
            self.entries[label].grid(row=i, column=1)

        #return self.entries['Type']  # initial focus

    def apply(self):
        self.result = {label: entry.get() for label, entry in self.entries.items()}

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry('1000x600')
        self.canvas = tk.Canvas(self, width=800, height=600, bg='white')
        self.canvas.pack(side='right')
        
        self.sidebar = tk.Frame(self, width=200, bg='#ddd', height=400, relief='sunken', borderwidth=2)
        self.sidebar.pack(expand=True, fill='both', side='left', anchor='nw')
        self.add_button = tk.Button(self.sidebar, text='Add Entry', command=self.show_add_entry_dialog)
        self.add_button.pack(pady=5)
        self.delete_button = tk.Button(self.sidebar, text='Delete Entry', command=self.delete_entry)
        self.delete_button.pack(pady=5)
        self.import_stl_button = tk.Button(self.sidebar, text='Import STL', command=self.import_stl)
        self.import_stl_button.pack(pady=5)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill='both', expand=True, side='right')
        self.title('3D Renderer')

        self.objects = []
        self.entries = []
        self.previous_mouse_x = None
        self.previous_mouse_y = None
        self.mouse_button_pressed = False

        self.camera_position = [0, 0, -5]
        self.camera_rotation = [0, 0]
        self.directional_light_direction_1 = normalize((2, 1, 1))
        self.directional_light_intensity = 1
        self.directional_light_direction_2 = normalize((-2, -1, -1))
        self.camera_light_intensity_factor = 10


        self.bind_events()

    
    def load_stl(self, filepath):
        stl_mesh = mesh.Mesh.from_file(filepath)
        vertices = []
        faces = []

        for i in range(len(stl_mesh.vectors)):
            face = []
            for j in range(3):  # STL files always have triangles
                vertex = tuple(stl_mesh.vectors[i][j])
                if vertex not in vertices:
                    vertices.append(vertex)
                    face.append(len(vertices) - 1)
                else:
                    face.append(vertices.index(vertex))
            faces.append(face)
        return vertices, faces
    
    
    def import_stl(self):
        filepath = filedialog.askopenfilename(filetypes=[('STL files', '*.stl')])
        dialog = AddEntryDialog(self, type_necessary=False)
        if filepath:
            try:     
                object_vertices, faces = self.load_stl(filepath)
                object_vertices = reshape(object_vertices, (float(dialog.result['scale_x']), float(dialog.result['scale_y']), float(dialog.result['scale_z'])))
                object_vertices = rotate_x(float(dialog.result['rot_x']), object_vertices)
                object_vertices = rotate_y(float(dialog.result['rot_y']), object_vertices)
                object_vertices = rotate_z(float(dialog.result['rot_z']), object_vertices)
                object_vertices = translate(object_vertices, (float(dialog.result['pos_x']), float(dialog.result['pos_y']), float(dialog.result['pos_z'])))
                self.objects.append(Object3D(object_vertices, faces))
                dialog_result_updated = dialog.result; dialog_result_updated['Type'] = 'STL Model'
                self.entries.append(dialog_result_updated)
                self.refresh_listbox()
            except Exception:
                pass

    def bind_events(self):
        self.canvas.bind('<Motion>', self.on_mouse_move)
        self.bind('<KeyPress>', self.on_key_press)
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_press)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_release)

    def show_add_entry_dialog(self):
        dialog = AddEntryDialog(self)
        if dialog.result:
            try:
                object_vertices = SHAPES[dialog.result['Type']]['vertices']
                object_vertices = reshape(object_vertices, (float(dialog.result['scale_x']), float(dialog.result['scale_y']), float(dialog.result['scale_z'])))
                object_vertices = rotate_x(float(dialog.result['rot_x']), object_vertices)
                object_vertices = rotate_y(float(dialog.result['rot_y']), object_vertices)
                object_vertices = rotate_z(float(dialog.result['rot_z']), object_vertices)
                object_vertices = translate(object_vertices, (float(dialog.result['pos_x']), float(dialog.result['pos_y']), float(dialog.result['pos_z'])))
                self.objects.append(Object3D(object_vertices, SHAPES[dialog.result['Type']]['faces']))
                self.entries.append(dialog.result)
            except Exception:
                pass
            self.refresh_listbox()
    
    def delete_entry(self):
        selected_indices = self.listbox.curselection()
        for index in selected_indices[::-1]:
            del self.entries[index]
        for index in selected_indices[::-1]:
            del self.objects[index]
        self.refresh_listbox()
    
    def refresh_listbox(self):
        self.listbox.delete(0, 'end')
        for entry in self.entries:
            self.listbox.insert('end', f"Type: {entry['Type']}, Position: ({entry['pos_x']}, {entry['pos_y']}, {entry['pos_z']})")
        self.draw()


    def on_mouse_press(self, event):
        self.mouse_button_pressed = True

    def on_mouse_release(self, event):
        self.mouse_button_pressed = False

    def on_mouse_move(self, event):
        if self.previous_mouse_x is not None and self.previous_mouse_y is not None and self.mouse_button_pressed:
            dx = event.x - self.previous_mouse_x
            dy = event.y - self.previous_mouse_y
            self.camera_rotation[0] += dx * 0.5
            self.camera_rotation[1] += dy * 0.5
            self.camera_rotation[1] = max(min(self.camera_rotation[1], 89), -89)
            self.draw()

        self.previous_mouse_x = event.x
        self.previous_mouse_y = event.y
    
    def on_key_press(self, event):
        step = 0.3
        rad_yaw = radians(self.camera_rotation[0])

        if event.keysym == 'w':
            self.camera_position[0] += sin(rad_yaw) * step
            self.camera_position[2] += cos(rad_yaw) * step
        elif event.keysym == 's':
            self.camera_position[0] -= sin(rad_yaw) * step
            self.camera_position[2] -= cos(rad_yaw) * step
        elif event.keysym == 'a':
            self.camera_position[0] -= cos(rad_yaw) * step
            self.camera_position[2] += sin(rad_yaw) * step
        elif event.keysym == 'd':
            self.camera_position[0] += cos(rad_yaw) * step
            self.camera_position[2] -= sin(rad_yaw) * step
        elif event.keysym == 'space':
            self.camera_position[1] += step
        elif event.keysym == 'Shift_L':
            self.camera_position[1] -= step

        self.draw()


    def project(self, vertex):
        x, y, z = translate([vertex], [-p for p in self.camera_position])[0]
        x, y, z = rotate_y(-self.camera_rotation[0], [(x, y, z)])[0]
        x, y, z = rotate_x(-self.camera_rotation[1], [(x, y, z)])[0] 
        near_clip_z = 0

        if z < near_clip_z:
            return None

        f = 200 / z
        return 400 + x * f, 300 - y * f
    
    def calculate_face_normal(self, face, obj):
        a, b, c = [obj.vertices[i] for i in face[:3]]
        u = vector_subtract(b, a)
        v = vector_subtract(c, a)
        return normalize(cross_product(u, v))

    def draw(self):
        self.canvas.delete('all')
        point_light_source = self.camera_position
        all_faces = []
        
        for obj in self.objects:
            for face in obj.faces:
                face_normal = self.calculate_face_normal(face, obj)
                camera_light_position = normalize(vector_subtract(point_light_source, obj.vertices[face[0]]))
                camera_intensity_point = dot_product(face_normal, camera_light_position)
                if camera_intensity_point > 0:
                    camera_intensity_point = min(camera_intensity_point, 1)
                    centroid = tuple(sum(obj.vertices[i][j] for i in face) / len(face) for j in range(3))
                    distance = sqrt(sum((point_light_source[i] - centroid[i])**2 for i in range(3)))
                    distance = max(distance, 5)
                    adjusted_intensity_point = min(max(camera_intensity_point * (self.camera_light_intensity_factor / (distance ** 2)), 0), 1)
                    intensity_directional_1 = dot_product(face_normal, self.directional_light_direction_1) * self.directional_light_intensity
                    intensity_directional_2 = dot_product(face_normal, self.directional_light_direction_2) * self.directional_light_intensity
                    intensity_directional_1, intensity_directional_2 = min(max(intensity_directional_1, 0), 1), min(max(intensity_directional_2, 0), 1)
                    intensity = intensity_directional_1 + intensity_directional_2 + adjusted_intensity_point
                    intensity = min(max(intensity, 0), 1)
                    distances = []
                    for vertex_index in face:
                        vertex = obj.vertices[vertex_index]
                        x, y, z = translate([vertex], [-p for p in self.camera_position])[0]
                        x, y, z = rotate_y(-self.camera_rotation[0], [(x, y, z)])[0]
                        x, y, z = rotate_x(-self.camera_rotation[1], [(x, y, z)])[0]
                        distance = sqrt(x**2 + y**2 + z**2)
                        distances.append(distance)
                    avg_distance = sum(distances) / len(distances)
                    all_faces.append((avg_distance, face, obj, intensity))
        
        all_faces.sort(reverse=True)
        for _, face, obj, intensity in all_faces:
            face_vertices = [self.project(obj.vertices[i]) for i in face if self.project(obj.vertices[i]) is not None]
            if len(face_vertices) >= 3:
                color = '#%02x%02x%02x' % (int(255 * intensity), int(255 * intensity), int(255 * intensity))
                self.canvas.create_polygon(face_vertices, fill=color)


if __name__ == '__main__':
    app = MainApp()
    app.after(100, app.draw)
    app.mainloop()