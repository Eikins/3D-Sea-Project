#version 330 core

out vec4 outColor;

uniform sampler2D _DiffuseMap;
uniform sampler2D _MoistMap;

uniform vec3 _MoistColor;

in vec2 _TexCoord0;

void main() {
    float moist = texture(_MoistMap, _TexCoord0).x;
    outColor = texture(_DiffuseMap, _TexCoord0) * (1.0 - moist) + vec4(moist * _MoistColor, 1.0);
}