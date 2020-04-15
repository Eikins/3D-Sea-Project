#version 410 core

out vec4 FragColor;

uniform vec3 _ViewPos;

uniform sampler2D _Noise;
uniform samplerCube _Skybox;

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

    vec3 noise = texture(_Noise, tes_out.TexCoord0 * 8.0).rgb;
    noise -= vec3(0.5, 0.0, 0.5);
    noise *= 0.5;

    vec3 normal     = tes_out.VertexNormal + noise;
    vec3 reflection = reflect(-viewDir, normal);
    // vec3 halfwayDir = normalize(lightDir + viewDir);
 
    // float spec = pow(max(dot(tes_out.VertexNormal, halfwayDir), 0.0), 8.0);
    // vec3 specular = vec3(1.0) * spec;

    // vec3 ambient = 0.00 * albedo.rgb;

    // float diff = max(dot(lightDir, tes_out.VertexNormal), 0.0);
    // vec3 diffuse = diff * albedo.rgb * 1.0;

    FragColor = vec4(texture(_Skybox, reflection).rgb, albedo.a);
}