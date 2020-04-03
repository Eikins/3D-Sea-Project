#version 330 core

uniform vec3 _Color = vec3(0.0, 0.0, 0.0);
uniform float _Atten = 1.0;

out vec4 FragColor;

void main() {
    FragColor = vec4(_Color * _Atten, 0.2);
}