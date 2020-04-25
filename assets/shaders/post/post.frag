#version 330 core

uniform sampler2D _MainTex;
uniform sampler2D _DepthTex;

uniform vec2 _ScreenSize;
uniform float _Time;
uniform vec3 _ViewPos;

in vec2 _TexCoord;

// CONSTANTS
#define WATER_LEVEL 5.25
#define MAX_DEPTH 25.25
vec3 _Color = vec3(0.37, 0.59, 0.85);

out vec4 FragColor;

void main(void) {
    vec3 color;

    float depthFactor = clamp((_ViewPos.y - (WATER_LEVEL - MAX_DEPTH)) / MAX_DEPTH, 0.0, 1.0);

    if(_ViewPos.y > WATER_LEVEL) {
        color = texture(_MainTex, _TexCoord).rgb;
    } else {
        vec3 fogColor = _Color * depthFactor;
        color = mix(texture(_MainTex, _TexCoord).rgb, fogColor, pow(texture(_DepthTex, _TexCoord).r, 40.0 * depthFactor + 10.0));
        color = depthFactor * color + (1.0 - depthFactor) * _Color * pow(depthFactor, 0.5);
    }

    color = pow(color, vec3(1.0 / 1.2));
    FragColor = vec4(color, 1.0);
}