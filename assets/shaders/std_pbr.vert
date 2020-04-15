#version 330 core

uniform mat4 _ProjectionMatrix;
uniform mat4 _ViewMatrix;
uniform mat4 _ModelMatrix;
uniform vec3 _ViewPos;
uniform vec3 _LightPos = vec3(20, 20, -20);

in vec3 InPosition;
in vec3 InNormal;
in vec3 InTangeant;
in vec2 InTexCoord0;
in vec2 InTexCoord1;
in vec2 InTexCoord2;
in vec2 InTexCoord3;
in vec2 InTexCoord4;
in vec2 InTexCoord5;
in vec2 InTexCoord6;
in vec2 InTexCoord7;

out vec3 _VertexPosition;
out vec3 _VertexNormal;
out vec3 _VertexTangeant;
out vec3 _VertexBitangeant;
out vec2 _TexCoord0;
out vec2 _TexCoord1;
out vec2 _TexCoord2;
out vec2 _TexCoord3;
out vec2 _TexCoord4;
out vec2 _TexCoord5;
out vec2 _TexCoord6;
out vec2 _TexCoord7;

void main() {
    gl_Position = _ProjectionMatrix * _ViewMatrix * _ModelMatrix * vec4(InPosition, 1.0);

    _VertexPosition = (_ModelMatrix * vec4(InPosition, 0.0)).xyz;

    _VertexNormal = normalize((_ModelMatrix * vec4(InNormal, 0.0)).xyz);
    _VertexTangeant = normalize((_ModelMatrix * vec4(InTangeant, 0.0)).xyz);
    _VertexBitangeant = cross(_VertexNormal, _VertexTangeant);

    _TexCoord0 = InTexCoord0;
    _TexCoord1 = InTexCoord1;
    _TexCoord2 = InTexCoord2;
    _TexCoord3 = InTexCoord3;
    _TexCoord4 = InTexCoord4;
    _TexCoord5 = InTexCoord5;
    _TexCoord6 = InTexCoord6;
    _TexCoord7 = InTexCoord7;
}