#version 410 core

uniform mat4 _ModelMatrix;
uniform mat4 _ViewMatrix;
uniform mat4 _ProjectionMatrix;

in vec3 InPosition;

out vec3 TexCoords;

void main() {
    TexCoords = InPosition;

    // Cancel translation
    mat4 view = _ViewMatrix;
    view[3] = vec4(0.0, 0.0, 0.0, 1.0);

    vec4 pos = _ProjectionMatrix * view * vec4(InPosition, 1.0);

    gl_Position = vec4(pos.xy, -pos.w, pos.w);
}