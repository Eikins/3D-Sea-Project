#version 410 core

uniform mat4 _ModelMatrix;
uniform mat4 _ViewMatrix;
uniform mat4 _ProjectionMatrix;

in vec3 InPosition;
in vec3 InNormal;
in vec3 InTangent;
in vec2 InTexCoord0;

out VertexData {
    vec3 VertexPosition;
    vec3 VertexNormal;
    vec3 VertexTangeant;
    vec2 TexCoord0;
} vs_out;


void main() {
    vs_out.VertexPosition = (_ModelMatrix * vec4(InPosition, 1.0)).xyz;

    vs_out.VertexNormal = normalize((_ModelMatrix * vec4(InNormal, 0.0)).xyz);
    vs_out.VertexTangeant = normalize((_ModelMatrix * vec4(InTangent, 0.0)).xyz);

    vs_out.TexCoord0 = InTexCoord0;
}