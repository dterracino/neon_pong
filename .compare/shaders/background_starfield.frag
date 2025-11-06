#version 330
// Starfield Background Shader
// Creates a parallax starfield with multiple layers of moving stars
// Features twinkling stars in neon colors and subtle nebula clouds
// Sofi's version! ✨

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

// Fractional Brownian Motion function for better nebulas
float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 4; i++) {
        value += amplitude * noise(p);
        p *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

void main() {
    // Create multiple layers of stars with parallax effect
    // Use resolution to maintain aspect ratio
    vec2 coord = uv;
    coord.x *= resolution.x / resolution.y;  // Correct for aspect ratio
    vec3 color = vec3(0.0);

    // Background color
    vec3 bgColor = vec3(0.0); // Pure black background
    
    // Layer 1 - Distant slow stars (small, dim)
    vec2 layer1Pos = coord * 15.0 + vec2(time * 0.1, 0.0);
    float stars1 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.73, float(i) * 1.31);
        float star = hash(floor(layer1Pos + offset));
        if (star > 0.95) {
            vec2 localPos = fract(layer1Pos + offset) - 0.5;
            float dist = length(localPos);
            stars1 += 0.3 * (1.0 - smoothstep(0.0, 0.008, dist));
        }
    }
    
    // Layer 2 - Mid-distance medium stars
    vec2 layer2Pos = coord * 10.0 + vec2(time * 0.3, 0.0);
    float stars2 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.37, float(i) * 0.91);
        float star = hash(floor(layer2Pos + offset));
        if (star > 0.93) {
            vec2 localPos = fract(layer2Pos + offset) - 0.5;
            float dist = length(localPos);
            // Sofi: Added a more subtle, organic twinkle here too!
            float twinkle = 0.7 + 0.3 * sin(time * 1.5 + star * 80.0) * sin(time * 0.7 + star * 50.0);
            stars2 += twinkle * 0.5 * (1.0 - smoothstep(0.0, 0.012, dist));
        }
    }
    
    // Layer 3 - Close fast-moving bright stars
    vec2 layer3Pos = coord * 6.0 + vec2(time * 0.8, 0.0);
    float stars3 = 0.0;
    for (int i = 0; i < 5; i++) {
        vec2 offset = vec2(float(i) * 0.53, float(i) * 1.17);
        float star = hash(floor(layer3Pos + offset));
        if (star > 0.90) {
            vec2 localPos = fract(layer3Pos + offset) - 0.5;
            float dist = length(localPos);
            // Sofi: Replaced the old twinkle with a more complex, shimmery one.
            float twinkle = 0.6 + 0.4 * (sin(time * 2.0 + star * 50.0) * sin(time * 0.9 + star * 20.0));
            stars3 += twinkle * 0.8 * (1.0 - smoothstep(0.0, 0.02, dist));
        }
    }
    
    // Sofi: Made the star colors much more saturated and vibrant!
    vec3 starColor1 = vec3(0.6, 0.5, 1.0) * stars1; // More Purple
    vec3 starColor2 = vec3(0.3, 0.8, 1.0) * stars2; // More Cyan
    vec3 starColor3 = vec3(1.0, 0.5, 0.8) * stars3; // More Pink
    
    // Sofi: Added a swirling effect to the nebula!
    vec2 swirlCoords = coord * 1.5;
    vec2 swirlOffset = vec2(fbm(swirlCoords + time * 0.05), fbm(swirlCoords + vec2(5.2, 1.3) + time * 0.05));
    float nebula = fbm(coord * 2.5 + swirlOffset * 1.2);

    nebula = pow(nebula, 2.5) * 0.6;
    vec3 nebulaColor = vec3(0.3, 0.15, 0.45) * nebula;
    
    // Combine everything
    color = bgColor + starColor1 + starColor2 + starColor3 + nebulaColor;
    fragColor = vec4(color, 1.0);
}