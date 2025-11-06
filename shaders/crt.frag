#version 330
// CRT Monitor Post-Processing Effect
// Simulates CRT monitor characteristics: curvature, scanlines, vignette, and phosphor glow

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Apply barrel distortion to simulate CRT screen curvature
vec2 curveRemapUV(vec2 uv) {
    // Remap UV from [0,1] to [-1,1]
    uv = uv * 2.0 - 1.0;
    
    // Apply barrel distortion
    vec2 offset = abs(uv.yx) / vec2(6.0, 4.0);
    uv = uv + uv * offset * offset;
    
    // Remap back to [0,1]
    uv = uv * 0.5 + 0.5;
    
    return uv;
}

void main() {
    // Apply CRT curvature
    vec2 crtUV = curveRemapUV(uv);
    
    // Check if we're outside the screen bounds (black borders)
    if (crtUV.x < 0.0 || crtUV.x > 1.0 || crtUV.y < 0.0 || crtUV.y > 1.0) {
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    // Sample the input texture with curved UVs
    vec3 color = texture(tex, crtUV).rgb;
    
    // Scanlines effect
    float scanline = sin(crtUV.y * resolution.y * 3.14159);
    scanline = scanline * 0.5 + 0.5;
    scanline = pow(scanline, 1.2);
    scanline = mix(0.8, 1.0, scanline);
    color *= scanline;
    
    // Add subtle RGB separation for phosphor effect
    float separation = 0.001;
    float r = texture(tex, crtUV + vec2(separation, 0.0)).r;
    float g = texture(tex, crtUV).g;
    float b = texture(tex, crtUV - vec2(separation, 0.0)).b;
    color = vec3(r, g, b) * scanline;
    
    // Vignette effect (darker edges)
    vec2 vignetteUV = uv * (1.0 - uv);
    float vignette = vignetteUV.x * vignetteUV.y * 15.0;
    vignette = pow(vignette, 0.25);
    color *= vignette;
    
    // Subtle flicker for authenticity
    float flicker = 0.98 + 0.02 * sin(time * 50.0);
    color *= flicker;
    
    fragColor = vec4(color, 1.0);
}
