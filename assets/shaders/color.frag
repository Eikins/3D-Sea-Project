#version 330 core

uniform vec3 _Color;
uniform float _Atten = 1.0;

out vec4 outColor;

void main() {
    outColor = vec4(_Color * _Atten, 1.0);
}