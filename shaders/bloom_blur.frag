#version 330

uniform sampler2D tex;
uniform bool horizontal;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Gaussian blur weights
const float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main() {
    vec2 tex_offset = 1.0 / resolution;
    vec3 result = texture(tex, uv).rgb * weight[0];
    
    if (horizontal) {
        for (int i = 1; i < 5; ++i) {
            result += texture(tex, uv + vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
            result += texture(tex, uv - vec2(tex_offset.x * i, 0.0)).rgb * weight[i];
        }
    } else {
        for (int i = 1; i < 5; ++i) {
            result += texture(tex, uv + vec2(0.0, tex_offset.y * i)).rgb * weight[i];
            result += texture(tex, uv - vec2(0.0, tex_offset.y * i)).rgb * weight[i];
        }
    }
    
    fragColor = vec4(result, 1.0);
}