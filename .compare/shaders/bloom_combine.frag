#version 330

uniform sampler2D scene;
uniform sampler2D bloom;
uniform float bloom_intensity;

in vec2 uv;
out vec4 fragColor;

void main() {
    vec3 scene_color = texture(scene, uv).rgb;
    vec3 bloom_color = texture(bloom, uv).rgb;
    
    // Additive blending with intensity
    vec3 result = scene_color + bloom_color * bloom_intensity;
    
    // Simple tone mapping
    result = result / (result + vec3(1.0));
    
    // Gamma correction
    result = pow(result, vec3(1.0 / 2.2));
    
    fragColor = vec4(result, 1.0);
}