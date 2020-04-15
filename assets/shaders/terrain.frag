#version 410 core

out vec4 FragColor;

const vec3 _WorldLightDir = normalize(vec3(0.0, 1.0, 0.0));

in VertexData {
    vec3 VertexPosition;
    vec3 VertexNormal;
    vec3 VertexTangeant;
    vec3 VertexBitangeant;
    vec2 TexCoord0;
} tes_out;

void main() {
    vec3 col = max(dot(_WorldLightDir, tes_out.VertexNormal), 0.0) * vec3(0.56, 0.47, 0.35);
    vec4 albedo = vec4(col, 1.0);

    FragColor = albedo;
}