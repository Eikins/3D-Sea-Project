#version 330 core

in vec2 _Coords;

out vec2 _TexCoord;

void main(void) {
  gl_Position = vec4(_Coords, 0.0, 1.0);
  _TexCoord = (_Coords + 1.0) / 2.0;
}