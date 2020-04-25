#version 410 core

uniform mat4 _ProjectionMatrix;
uniform mat4 _ViewMatrix;
uniform mat4 _ModelMatrix;
uniform vec3 _ViewPos;


in vec3 InPosition;
in vec3 InNormal;
in vec3 InTangent;
in vec2 InTexCoord0;

out VertexOutput {
    vec3 Position;
    vec3 Normal;
    vec3 Tangent;
    vec2 TexCoord0;
} vs_out;


void main() {
    vs_out.Position = (_ModelMatrix * vec4(InPosition, 1.0)).xyz;
    vs_out.Normal = normalize((_ModelMatrix * vec4(InNormal, 0.0)).xyz);
    vs_out.Tangent = normalize((_ModelMatrix * vec4(InTangent, 0.0)).xyz);
    vs_out.TexCoord0 = InTexCoord0;

    gl_Position = _ProjectionMatrix * _ViewMatrix * vec4(vs_out.Position, 1.0);
}