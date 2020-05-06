#version 410 core

out vec4 FragColor;

uniform vec3 _ViewPos;

uniform sampler2D _Normal;
uniform samplerCube _Skybox;
uniform float _Time;

#define WIND vec2(0.15, -0.2)

const vec3 _WorldLightDir = normalize(vec3(-0.5, -1, -0.5));

in VertexData {
    vec3 VertexPosition;
    vec3 VertexNormal;
    vec3 VertexTangeant;
    vec2 TexCoord0;
} tes_out;

#define PI 3.14159265359
#define SQRT_PI 1.77245385091
// ==== BRDF ===========================================================
// http://graphicrants.blogspot.com/2013/08/specular-brdf-reference.html
float ConvertRoughness(float roughness) {
    return roughness * roughness;
}

float DistributionGGX_Isotropic(float NdotH, float roughness) {
    float sqrt_res = roughness / (SQRT_PI * (NdotH * NdotH * (roughness * roughness - 1.0) + 1.0));
    return sqrt_res * sqrt_res;
}

float GeometrySchlickGGX(float NdotV, float roughness) {
    float k = roughness / 2.0;
    return NdotV / (NdotV * (1 - k) + k);
}

float GeometrySmith(float NdotV, float NdotL, float roughness) {
    return GeometrySchlickGGX(NdotV, roughness) * GeometrySchlickGGX(NdotL, roughness);
}


vec3 FresnelSchlick(float VdotH, vec3 F0) {
    // 0.000001 to avoid negative approx
    return F0 + (1 - F0) * pow(1 + 0.000001 - VdotH, 5);
}


// ==== HDR ============================
vec3 GammaToLinear(in vec3 color) {
    return pow(color, vec3(2.2));
}

vec3 LinearToGamma(in vec3 color) {
    return pow(color, vec3(1.0 / 2.2));
}
// =====================================

vec3 GetNormal() {
    vec3 normal = normalize(tes_out.VertexNormal);
    vec3 tangent = normalize(tes_out.VertexTangeant);
    vec3 bitangent = cross(normal, tangent);

    mat3 TBN = mat3(tangent, bitangent, normal);

    vec3 sampledNormal = texture(_Normal, tes_out.TexCoord0 * 125.0 - WIND * _Time).rgb;
    sampledNormal = normalize(sampledNormal * 2.0 - 1.0); 
    return TBN * sampledNormal;
}

void main() {

    vec3 baseColor = vec3(0.43, 0.73, 1.0);
    float roughness = 0.15;
    float metalness = 0.0;
    float ambienOcclusion = 1.0;

    baseColor = GammaToLinear(baseColor);
    roughness = clamp(roughness, 0.01, 0.99);
    roughness = ConvertRoughness(roughness);

    vec3 normal = GetNormal();
    vec3 view = normalize(_ViewPos - tes_out.VertexPosition);
    vec3 reflection = reflect(-view, normal);

    float NdotV = max(dot(normal, view), 0.0);
    // 0.04 is the approximated fresnel term for dielectric materials
    vec3 F0 = mix(vec3(0.04), baseColor, metalness);

    // Direct Lighting
    vec3 direct = vec3(0.0);

    for (int i = 0; i < 1; i++) {
        vec3 light = -_WorldLightDir;
        vec3 halfway = normalize(light + view);

        float NdotL = max(dot(normal, light), 0.0);
        float NdotH = max(dot(normal, halfway), 0.0);
        float VdotH = max(dot(view, halfway), 0.0);

        // Cook-Torrance BRDF: http://graphicrants.blogspot.com/2013/08/specular-brdf-reference.html
        float D = DistributionGGX_Isotropic(NdotH, roughness);
        vec3 F = FresnelSchlick(VdotH, F0);
        float G = GeometrySmith(NdotV, NdotL, roughness);

        vec3 specular = (D * F * G) / (4.0 * NdotL * NdotV + 0.00001);
        // Energy conservation, multiply the baseColor by the absorption
        vec3 diffuse = (baseColor / PI) * (1.0 - F) * (1.0 - metalness);
        direct += (diffuse + specular) * vec3(1.0) * NdotL;
    }

    vec3 indirect = texture(_Skybox, reflection).rgb * 0.15 + baseColor * 0.15;

    vec3 color = (direct + indirect) * ambienOcclusion;
    FragColor = vec4(LinearToGamma(color), 0.7);

    //FragColor = vec4(tes_out.VertexNormal, 1.0);


    /*
    vec4 albedo = vec4(0.43, 0.73, 1.0, 0.7);
    
    vec3 lightDir   = -_WorldLightDir;
    vec3 viewDir    = normalize(_ViewPos - tes_out.VertexPosition);

    vec3 noise = texture(_Noise, tes_out.TexCoord0 * 125.0 + NOISE_DIR * _Time).rgb;
    noise -= vec3(0.5, 0.0, 0.5);
    noise *= 0.5;

    vec3 normal     = tes_out.VertexNormal + noise;
    vec3 reflection = reflect(-viewDir, normal);

    FragColor = vec4(texture(_Skybox, reflection).rgb * 0.7 + albedo.rgb * 0.3, albedo.a);*/
}