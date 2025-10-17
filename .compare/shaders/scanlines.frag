#version 330
// Scanlines Post-Processing Effect
// Adds horizontal scanlines effect typical of retro CRT monitors

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

void main() {
    // Sample the input texture
    vec3 color = texture(tex, uv).rgb;
    
    // Calculate scanline intensity
    // Using screen coordinates to create consistent line width
    float scanline = sin(uv.y * resolution.y * 3.14159);
    scanline = scanline * 0.5 + 0.5;
    
    // Make scanlines more pronounced
    scanline = pow(scanline, 1.5);
    
    // Mix between 0.7 and 1.0 to avoid completely dark lines
    scanline = mix(0.7, 1.0, scanline);
    
    // Apply scanlines to color
    color *= scanline;
    
    // Slight brightness boost to compensate for darkening
    color *= 1.1;
    
    fragColor = vec4(color, 1.0);
}
