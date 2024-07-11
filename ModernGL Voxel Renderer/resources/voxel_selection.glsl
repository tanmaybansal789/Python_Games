#version 330 core

#if defined VERTEX_SHADER

uniform mat4 m_proj;
uniform mat4 m_camera;
uniform mat4 m_model;

layout(location = 0) in vec3 in_position;
void main() {
    gl_Position = m_proj * m_camera * m_model * vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER

out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 0.0, 0.0, 1.0);  // Red color
}

#endif