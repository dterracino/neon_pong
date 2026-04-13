#version 330
// Scanlines Post-Processing Effect
// Adds horizontal scanlines effect typical of retro CRT monitors

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;
uniform float scanlineThickness;  // Pixels per scanline pair

in vec2 uv;
out vec4 fragColor;

void main() {
    // Sample the input texture
    vec3 color = texture(tex, uv).rgb;

    // One full sine cycle per (scanlineThickness) pixels
    // Higher thickness = lower frequency = fatter bands
    float freq = resolution.y / scanlineThickness;
    float scanline = sin(uv.y * freq * 3.14159);
    scanline = scanline * 0.5 + 0.5;

    // Higher power = wider dark troughs relative to bright peaks
    scanline = pow(scanline, 3.0);

    // Mix between 0.55 (dark trough) and 1.0 (bright peak)
    scanline = mix(0.55, 1.0, scanline);

    // Apply scanlines to color
    color *= scanline;

    // Slight brightness boost to compensate for darkening
    color *= 1.15;

    fragColor = vec4(color, 1.0);
}
