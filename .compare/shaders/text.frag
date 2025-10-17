#version 330

uniform sampler2D tex;
uniform vec4 color;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 texColor = texture(tex, uv);
    fragColor = texColor * color;
}
