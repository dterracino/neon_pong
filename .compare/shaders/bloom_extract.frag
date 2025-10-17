#version 330

uniform sampler2D tex;
uniform float threshold;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec4 color = texture(tex, uv);
    
    // Calculate luminance
    float luminance = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    
    // Extract bright pixels above threshold
    if (luminance > threshold) {
        fragColor = color;
    } else {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
}