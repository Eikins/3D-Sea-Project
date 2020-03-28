#version 330 core

uniform mat4 _ProjectionViewMatrix;
uniform mat4 _ModelMatrix;

layout(location = 0) in vec3 _position;
layout(location = 1) in vec3 _normal;

out vec3 _VertexNormal;
out vec3 _VertexPosition;

void main() {
    gl_Position = _ProjectionViewMatrix * _ModelMatrix * vec4(_position, 1.0);
    _VertexNormal = normalize(vec3(_ModelMatrix * vec4(_normal, 1.0)));
    _VertexPosition = _position;
}