#version 330
// Plasma Background Shader
// Creates a smooth flowing plasma effect with neon colors
// Multiple sine waves create organic, hypnotic movement

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Smooth plasma effect with neon colors
void main() {
    vec2 coord = uv * 2.0 - 1.0;
    coord.x *= resolution.x / resolution.y;
    
    // Create multiple moving sine waves for plasma effect
    float value = 0.0;
    
    // Wave 1 - horizontal movement
    value += sin(coord.x * 3.0 + time * 0.5);
    
    // Wave 2 - vertical movement
    value += sin(coord.y * 3.0 - time * 0.7);
    
    // Wave 3 - diagonal movement
    value += sin((coord.x + coord.y) * 2.0 + time * 0.3);
    
    // Wave 4 - circular movement
    value += sin(length(coord) * 4.0 - time);
    
    // Wave 5 - complex swirl
    value += sin(atan(coord.y, coord.x) * 5.0 + time * 0.5 + length(coord) * 2.0);
    
    // Normalize the value
    value = value / 5.0;
    
    // Map to neon color palette (dark purple -> pink -> cyan)
    vec3 color1 = vec3(0.05, 0.02, 0.15);  // Dark purple background
    vec3 color2 = vec3(0.4, 0.15, 0.5);    // Purple
    vec3 color3 = vec3(1.0, 0.44, 0.81);   // Neon pink
    vec3 color4 = vec3(0.0, 0.8, 0.996);   // Cyan
    
    // Create smooth color transitions
    vec3 color;
    float t = (value + 1.0) * 0.5; // Map from [-1,1] to [0,1]
    
    if (t < 0.33) {
        color = mix(color1, color2, t * 3.0);
    } else if (t < 0.66) {
        color = mix(color2, color3, (t - 0.33) * 3.0);
    } else {
        color = mix(color3, color4, (t - 0.66) * 3.0);
    }
    
    // Darken the colors to make them less intrusive (30% of original brightness)
    color *= 0.3;
    
    // Add some subtle brightness variation for depth
    float depth = 0.8 + 0.2 * sin(time * 0.2 + length(coord) * 2.0);
    color *= depth;
    
    fragColor = vec4(color, 1.0);
}
