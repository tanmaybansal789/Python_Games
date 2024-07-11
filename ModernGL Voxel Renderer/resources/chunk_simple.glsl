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

vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract(p3.xxy + p3.yzz);
}

void main() {
    color = hash31(voxel_id);
    gl_Position = m_proj * m_camera * m_model * vec4(in_position, 1.0);
    //color = vec3(face_id * 0.1);
}

#elif defined FRAGMENT_SHADER

// Fragment shader
in vec3 color;
out vec4 fragColor;

void main() {
    // Apply a shade based on the face_id to create a simple lighting effect
    fragColor = vec4(color, 1.0);
}

#endif