#version 330 core

out vec4 outColor;

// ==== Properties ====
uniform sampler2D _AlbedoMap;
uniform sampler2D _NormalMap;
uniform float _Emission = 0.05;
uniform float _Diffusion = 0.5;
uniform float _Shininess = 8.0;

uniform vec3 _ViewPos;
uniform vec3 _LightPos = vec3(20, 20, -20);

const vec3 _WorldLightDir = -normalize(vec3(-0.5, -1, 0.5));

in vec3 _VertexPosition;
in vec3 _VertexNormal;
in vec3 _VertexTangeant;
in vec3 _VertexBitangeant;

in vec2 _TexCoord0;

void main() {

    vec4 albedo = texture(_AlbedoMap, _TexCoord0).rgba;
    
    vec3 normal = texture(_NormalMap, _TexCoord0).rgb;
    normal = normalize(normal * 2.0 - 1.0); 

    vec3 lightDir   = _WorldLightDir;
    vec3 viewDir    = normalize(_ViewPos - _VertexPosition);
    vec3 halfwayDir = normalize(lightDir + viewDir);

    mat3 invTBN = mat3(_VertexTangeant, _VertexBitangeant, _VertexNormal);
    // lightDir = invTBN * lightDir;
    // viewDir = invTBN * viewDir;
    // halfwayDir = invTBN * halfwayDir;
    normal = invTBN * normal;
 
    float spec = pow(max(dot(normal, halfwayDir), 0.0), _Shininess);
    vec3 specular = vec3(0.3) * spec;

    vec3 ambient = _Emission * albedo.rgb;

    float diff = max(dot(lightDir, normal), 0.0);
    vec3 diffuse = diff * albedo.rgb * _Diffusion;

    outColor = vec4(ambient + diffuse + specular, albedo.a);

}