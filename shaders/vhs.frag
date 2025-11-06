#version 330
// VHS Tape Post-Processing Effect
// Simulates VHS tape artifacts: chromatic aberration, noise, distortion, tracking lines

uniform sampler2D tex;
uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Hash function for noise generation
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// Noise function
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void main() {
    vec2 distortedUV = uv;
    
    // VHS tracking distortion - horizontal bands that shift
    float trackingNoise = noise(vec2(uv.y * 10.0, time * 0.5));
    float trackingShift = (trackingNoise - 0.5) * 0.01;
    
    // Random tracking glitches
    float glitchBand = step(0.98, hash(vec2(floor(uv.y * 20.0), floor(time * 2.0))));
    trackingShift += glitchBand * (hash(vec2(time * 10.0, uv.y)) - 0.5) * 0.05;
    
    distortedUV.x += trackingShift;
    
    // VHS chromatic aberration - RGB separation
    float aberration = 0.003 + trackingNoise * 0.002;
    float r = texture(tex, distortedUV + vec2(aberration, 0.0)).r;
    float g = texture(tex, distortedUV).g;
    float b = texture(tex, distortedUV - vec2(aberration, 0.0)).b;
    vec3 color = vec3(r, g, b);
    
    // VHS tape noise (film grain)
    float grainAmount = 0.05;
    float grain = hash(uv * time) * 2.0 - 1.0;
    color += grain * grainAmount;
    
    // Horizontal sync lines (occasional)
    float syncLine = step(0.99, hash(vec2(floor(uv.y * 200.0), floor(time * 5.0))));
    color += vec3(syncLine * 0.3);
    
    // Color bleeding/ghosting
    vec3 ghost = texture(tex, distortedUV + vec2(-0.002, 0.0)).rgb;
    color = mix(color, ghost, 0.15);
    
    // VHS color degradation - slightly desaturated with color shift
    float luminance = dot(color, vec3(0.299, 0.587, 0.114));
    color = mix(color, vec3(luminance), 0.15);
    
    // Slight yellow/magenta tint typical of old VHS
    color.r *= 1.05;
    color.b *= 0.98;
    
    // Bottom edge noise (common in VHS)
    if (uv.y > 0.95) {
        float edgeNoise = noise(vec2(uv.x * 100.0, time * 10.0));
        color = mix(color, vec3(edgeNoise), 0.3);
    }
    
    fragColor = vec4(color, 1.0);
}
