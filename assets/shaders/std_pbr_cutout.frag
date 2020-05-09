#version 410 core

out vec4 FragColor;

// ==== Properties ====
uniform sampler2D _Albedo;
uniform sampler2D _Normal;
uniform sampler2D _Roughness;
uniform sampler2D _Metalness;
uniform sampler2D _AmbientOcclusion;

uniform samplerCube _ReflectionProbe;

uniform float _AlphaCutoutThreshold = 0.5;


uniform vec3 _ViewPos;

const vec3 _WorldLightDir = normalize(vec3(-0.5, -1, -0.5));

in VertexOutput {
    vec3 Position;
    vec3 Normal;
    vec3 Tangent;
    vec2 TexCoord0;
} vs_out;

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
    vec3 normal = normalize(vs_out.Normal);
    vec3 tangent = normalize(vs_out.Tangent);
    vec3 bitangent = cross(normal, tangent);

    mat3 TBN = mat3(tangent, bitangent, normal);

    vec3 sampledNormal = texture(_Normal, vs_out.TexCoord0).rgb;
    sampledNormal = normalize(sampledNormal * 2.0 - 1.0); 
    return TBN * sampledNormal;
}

void main() {

    vec4 albedo = texture(_Albedo, vs_out.TexCoord0);
    vec3 baseColor = albedo.rgb;

    if(albedo.a <= _AlphaCutoutThreshold) {
        discard;
    }

    float roughness = texture(_Roughness, vs_out.TexCoord0).r;
    float metalness = texture(_Metalness, vs_out.TexCoord0).r;
    float ambienOcclusion = texture(_AmbientOcclusion, vs_out.TexCoord0).r;

    baseColor = GammaToLinear(baseColor);
    roughness = clamp(roughness, 0.01, 0.99);
    roughness = ConvertRoughness(roughness);

    vec3 normal = GetNormal();
    vec3 view = normalize(_ViewPos - vs_out.Position);
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

    vec3 indirect = vec3(0.03) * baseColor + (texture(_ReflectionProbe, reflection).rgb * 0.02 * metalness);

    vec3 color = (direct + indirect) * ambienOcclusion;
    FragColor = vec4(LinearToGamma(color), 1.0);

}