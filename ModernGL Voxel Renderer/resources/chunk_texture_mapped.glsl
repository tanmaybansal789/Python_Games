#version 330 core

#if defined VERTEX_SHADER

// Vertex shader
layout(location = 0) in vec3 in_position;
layout(location = 1) in uint voxel_id;
layout(location = 2) in uint face_id;
layout(location = 3) in vec2 in_texcoord;

uniform mat4 m_proj;
uniform mat4 m_camera;
uniform mat4 m_model;

out vec3 frag_tex_array_coord;
out float shade;


void main() {
    gl_Position = m_proj * m_camera * m_model * vec4(in_position, 1.0);

    // Shading based on face_id
    switch (face_id) {
        case 0: shade = 1.0; break; // top face, fully lit
        case 1: shade = 0.3; break; // bottom face, darker
        case 2: shade = 0.7; break; // left face, medium light
        case 3: shade = 0.7; break; // right face, medium light
        case 4: shade = 0.9; break; // front face, slightly dim
        case 5: shade = 0.5; break; // back face, dim
        default: shade = 1.0; break;
    }

    frag_tex_array_coord = vec3((in_texcoord.x + min(face_id, 2)) / 3.0, in_texcoord.y, int(voxel_id) - 1);

}

#elif defined FRAGMENT_SHADER

// Fragment shader
in vec3 frag_tex_array_coord;
in float shade;

uniform sampler2DArray u_texture_array_0;

out vec4 frag_color;

void main() {
    //frag_color = vec4(v_texcoord, 0.0, 1.0);  // Apply the shade factor to color
    frag_color = texture(u_texture_array_0, frag_tex_array_coord) * shade;
}

#endif
