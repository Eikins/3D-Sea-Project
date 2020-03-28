#version 330 core

out vec4 outColor;

in vec3 _VertexNormal;

const vec3 LIGHT_DIR = normalize(vec3(1.0));

void main() {
    outColor = dot(-LIGHT_DIR, _VertexNormal) *  vec4(0.0, 0.0, 1.0, 1.0);
}