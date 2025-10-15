#version 330
// Dust Overlay Shader
// Creates meandering dust particles with random glinting
// Rendered as a transparent overlay on top of background

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Hash function for pseudo-random numbers (better distribution)
float hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

float hash2(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// 2D noise function
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = hash2(i);
    float b = hash2(i + vec2(1.0, 0.0));
    float c = hash2(i + vec2(0.0, 1.0));
    float d = hash2(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal Brownian Motion for smooth organic movement
float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < 4; i++) {
        value += amplitude * noise(p * frequency);
        amplitude *= 0.5;
        frequency *= 2.0;
    }
    
    return value;
}

void main() {
    vec3 color = vec3(0.0);
    float totalAlpha = 0.0;
    
    // Create simple wandering dust particles with random walk behavior
    // Reduced from 50 to 15 particles for much better performance
    for (int i = 0; i < 15; i++) {
        float particleId = float(i) + 1.0;
        
        // Better distributed starting positions using different hash seeds
        float startX = hash(particleId * 73.156);
        float startY = hash(particleId * 157.392);
        
        // Each particle has random initial direction (0 to 2*PI)
        float initialAngle = hash(particleId * 241.873) * 6.28318;
        
        // Base movement speed (slow drift)
        float baseSpeed = 0.02 + hash(particleId * 319.642) * 0.02;
        
        // Simulate random walk with direction changes
        // Sample noise at different time intervals to get direction changes
        // Higher frequency = more frequent direction changes (roughly 10% chance per "interval")
        float directionChangeRate = 0.1; // Controls how often direction changes
        float timeScale = time * 0.5; // Slow down time for smoother motion
        
        // Use noise to determine direction changes over time
        // Multiple octaves create the ~10% random change behavior
        float angleOffset = 0.0;
        for (int octave = 0; octave < 8; octave++) {
            float freq = pow(2.0, float(octave)) * directionChangeRate;
            float noiseVal = noise(vec2(particleId * 0.1, timeScale * freq));
            
            // Convert noise to angle change (±22.5 degrees = ±0.3927 radians)
            // Weight decreases with each octave for smoother motion
            float weight = 1.0 / pow(2.0, float(octave));
            angleOffset += (noiseVal - 0.5) * 0.785 * weight; // 0.785 = 45 degrees total range
        }
        
        // Current angle is initial angle plus accumulated changes
        float currentAngle = initialAngle + angleOffset;
        
        // Calculate velocity from angle
        vec2 velocity = vec2(cos(currentAngle), sin(currentAngle)) * baseSpeed;
        
        // Integrate velocity over time to get position
        vec2 displacement = velocity * time;
        
        // Particle position (wraps around screen)
        vec2 particlePos = vec2(
            mod(startX + displacement.x, 1.0),
            mod(startY + displacement.y, 1.0)
        );
        
        // Distance from current pixel to particle
        vec2 diff = uv - particlePos;
        
        // Handle wrapping (distance to nearest instance including wrapped edges)
        if (diff.x > 0.5) diff.x -= 1.0;
        if (diff.x < -0.5) diff.x += 1.0;
        if (diff.y > 0.5) diff.y -= 1.0;
        if (diff.y < -0.5) diff.y += 1.0;
        
        // Correct for aspect ratio
        diff.x *= resolution.x / resolution.y;
        float dist = length(diff);
        
        // Particle size (varies per particle)
        float particleSize = 0.008 + hash(particleId * 431.127) * 0.012;
        
        // Create soft particle
        float particle = 1.0 - smoothstep(0.0, particleSize, dist);
        
        // Add glinting effect (each particle glints at different times)
        float glintPhase = time * 2.0 + particleId * 0.571;
        float glint = pow(max(0.0, sin(glintPhase)), 8.0);
        
        // Base brightness + glint
        float brightness = 0.25 + glint * 0.6;
        
        // Random color tint per particle
        float colorSeed = hash(particleId * 523.846);
        vec3 dustColor;
        if (colorSeed < 0.33) {
            dustColor = vec3(0.9, 0.85, 1.0); // Blue-white
        } else if (colorSeed < 0.66) {
            dustColor = vec3(1.0, 0.9, 0.95); // Pink-white
        } else {
            dustColor = vec3(0.85, 0.9, 1.0); // Cyan-white
        }
        
        color += dustColor * particle * brightness;
        totalAlpha += particle * brightness;
    }
    
    // Clamp alpha to reasonable range
    totalAlpha = min(totalAlpha, 0.4);
    
    // Output with transparency
    fragColor = vec4(color, totalAlpha);
}
