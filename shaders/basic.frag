#version 330

uniform sampler2D tex;
uniform vec4 color;

in vec2 uv;
out vec4 fragColor;

void main() {
    fragColor = color;
}