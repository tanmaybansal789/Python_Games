#version 330 core

#if defined VERTEX_SHADER

// Vertex shader
layout(location = 0) in vec3 in_position;
layout(location = 1) in uint voxel_id;
layout(location = 2) in uint face_id;

uniform mat4 m_proj;
uniform mat4 m_camera;
uniform mat4 m_model;

out vec3 color;
out float shade;

vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract(p3.xxy + p3.yzz);
}

void main() {
    color = hash31(voxel_id);
    gl_Position = m_proj * m_camera * m_model * vec4(in_position, 1.0);

    // Shading based on face_id
    switch (face_id) {
        case 0: shade = 1.0; break; // top face, fully lit
        case 1: shade = 0.5; break; // bottom face, darker
        case 2: shade = 0.8; break; // left face, medium light
        case 3: shade = 0.8; break; // right face, medium light
        case 4: shade = 0.9; break; // front face, slightly dim
        case 5: shade = 0.7; break; // back face, dim
        default: shade = 1.0; break;
    }
}

#elif defined FRAGMENT_SHADER

// Fragment shader
in vec3 color;
in float shade;
out vec4 fragColor;

void main() {
    fragColor = vec4(color * shade, 1.0);  // Apply the shade factor to color
}

#endif
