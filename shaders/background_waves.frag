#version 330
// Waves Background Shader
// Creates animated wave patterns with a retro grid overlay
// Cyan/pink waves for that classic synthwave aesthetic

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

void main() {
    // Create animated wave pattern
    vec2 coord = uv * 2.0 - 1.0;
    coord.x *= resolution.x / resolution.y;
    
    // Background gradient
    vec3 bgColor = vec3(0.05, 0.02, 0.15) + vec3(0.0, 0.0, 0.05) * uv.y;
    
    // Multiple wave layers
    float wave = 0.0;
    
    // Horizontal waves
    wave += sin(uv.y * 10.0 + time * 1.5) * 0.5;
    wave += sin(uv.y * 6.0 - time * 1.0) * 0.3;
    
    // Vertical waves
    wave += sin(uv.x * 8.0 + time * 1.2) * 0.4;
    
    // Create color based on wave intensity
    vec3 waveColor = vec3(0.0);
    if (wave > 0.0) {
        // Positive waves are cyan
        waveColor = vec3(0.0, 0.8, 0.996) * wave * 0.15;
    } else {
        // Negative waves are pink
        waveColor = vec3(1.0, 0.44, 0.81) * (-wave) * 0.15;
    }
    
    // Add some grid lines
    float gridX = abs(sin(uv.x * 20.0));
    float gridY = abs(sin(uv.y * 20.0));
    float grid = (gridX < 0.05 || gridY < 0.05) ? 0.1 : 0.0;
    vec3 gridColor = vec3(0.3, 0.2, 0.5) * grid;
    
    // Combine all elements
    vec3 color = bgColor + waveColor + gridColor;
    
    fragColor = vec4(color, 1.0);
}
