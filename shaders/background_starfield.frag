#version 330

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Hash function for pseudo-random numbers
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
    // Create multiple layers of stars with parallax effect
    vec2 coord = uv;
    vec3 color = vec3(0.0);
    
    // Background gradient - dark purple to darker purple
    vec3 bgColor = vec3(0.05, 0.02, 0.15) + vec3(0.02, 0.01, 0.05) * (1.0 - uv.y);
    
    // Layer 1 - Distant slow stars (small, dim)
    vec2 layer1Pos = coord * 15.0 + vec2(time * 0.01, 0.0);
    float stars1 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.73, float(i) * 1.31);
        float star = hash(floor(layer1Pos + offset));
        if (star > 0.95) {
            vec2 localPos = fract(layer1Pos + offset) - 0.5;
            float dist = length(localPos);
            stars1 += 0.3 * (1.0 - smoothstep(0.0, 0.02, dist));
        }
    }
    
    // Layer 2 - Mid-distance medium stars
    vec2 layer2Pos = coord * 10.0 + vec2(time * 0.03, 0.0);
    float stars2 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.37, float(i) * 0.91);
        float star = hash(floor(layer2Pos + offset));
        if (star > 0.93) {
            vec2 localPos = fract(layer2Pos + offset) - 0.5;
            float dist = length(localPos);
            stars2 += 0.5 * (1.0 - smoothstep(0.0, 0.03, dist));
        }
    }
    
    // Layer 3 - Close fast-moving bright stars
    vec2 layer3Pos = coord * 6.0 + vec2(time * 0.08, 0.0);
    float stars3 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.53, float(i) * 1.17);
        float star = hash(floor(layer3Pos + offset));
        if (star > 0.90) {
            vec2 localPos = fract(layer3Pos + offset) - 0.5;
            float dist = length(localPos);
            // Add some twinkling
            float twinkle = 0.7 + 0.3 * sin(time * 3.0 + star * 100.0);
            stars3 += twinkle * 0.8 * (1.0 - smoothstep(0.0, 0.05, dist));
        }
    }
    
    // Combine star layers with different colors (cyan/pink/purple tints)
    vec3 starColor1 = vec3(0.8, 0.7, 1.0) * stars1;  // Purple-ish
    vec3 starColor2 = vec3(0.6, 0.9, 1.0) * stars2;  // Cyan-ish
    vec3 starColor3 = vec3(1.0, 0.8, 0.9) * stars3;  // Pink-ish
    
    // Add some subtle nebula-like clouds
    float nebula = noise(coord * 3.0 + vec2(time * 0.005, 0.0));
    nebula = pow(nebula, 3.0) * 0.1;
    vec3 nebulaColor = vec3(0.2, 0.1, 0.3) * nebula;
    
    // Combine everything
    color = bgColor + starColor1 + starColor2 + starColor3 + nebulaColor;
    
    fragColor = vec4(color, 1.0);
}
