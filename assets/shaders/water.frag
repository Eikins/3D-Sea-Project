#version 410 core

out vec4 FragColor;

uniform vec3 _ViewPos;

uniform sampler2D _Noise;
uniform samplerCube _Skybox;
uniform float _Time;

#define NOISE_DIR vec2(0.15, -0.2)

const vec3 _WorldLightDir = normalize(vec3(1.0, 1.0, 1.0));

in VertexData {
    vec3 VertexPosition;
    vec3 VertexNormal;
    vec3 VertexTangeant;
    vec3 VertexBitangeant;
    vec2 TexCoord0;
} tes_out;

void main() {

    vec4 albedo = vec4(0.43, 0.73, 1.0, 0.7);
    
    vec3 lightDir   = -_WorldLightDir;
    vec3 viewDir    = normalize(_ViewPos - tes_out.VertexPosition);

    vec3 noise = texture(_Noise, tes_out.TexCoord0 * 125.0 + NOISE_DIR * _Time).rgb;
    noise -= vec3(0.5, 0.0, 0.5);
    noise *= 0.5;

    vec3 normal     = tes_out.VertexNormal + noise;
    vec3 reflection = reflect(-viewDir, normal);

    FragColor = vec4(texture(_Skybox, reflection).rgb * 0.7 + albedo.rgb * 0.3, albedo.a);
}