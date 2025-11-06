#version 330
// Retrowave Background Shader
// Creates a classic retrowave/synthwave aesthetic with:
// - Perspective grid floor
// - Wireframe mountains
// - Large sun with horizontal stripes
// - Starfield
// - Scan lines for CRT effect

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Constants for retrowave look
const vec3 COLOR_SKY_TOP = vec3(0.05, 0.02, 0.15);      // Dark purple
const vec3 COLOR_SKY_HORIZON = vec3(0.4, 0.15, 0.5);    // Purple
const vec3 COLOR_SUN_TOP = vec3(1.0, 0.95, 0.3);        // Yellow
const vec3 COLOR_SUN_MID = vec3(1.0, 0.6, 0.2);         // Orange
const vec3 COLOR_SUN_BOTTOM = vec3(1.0, 0.2, 0.4);      // Pink
const vec3 COLOR_GRID = vec3(1.0, 0.2, 0.6);            // Magenta/Pink
const vec3 COLOR_MOUNTAIN = vec3(0.0, 0.8, 0.996);      // Cyan
const vec3 COLOR_FLOOR = vec3(0.02, 0.01, 0.08);        // Very dark purple

const float HORIZON = 0.5;  // Horizon line position (0-1)
const float GRID_SIZE = 0.08; // Grid cell size
const float GRID_LINE_WIDTH = 0.015;
const float SUN_SIZE = 0.22;
const float SUN_Y_POS = 0.65;

// Hash function for pseudo-random numbers
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// Simple noise function for mountains
float noise(float x) {
    float i = floor(x);
    float f = fract(x);
    float u = f * f * (3.0 - 2.0 * f);
    return mix(hash(vec2(i, 0.0)), hash(vec2(i + 1.0, 0.0)), u);
}

// Generate mountain height at given x position
float mountainHeight(float x, float layer) {
    float height = 0.0;
    float freq = 2.0 + layer;
    height += noise(x * freq) * 0.15;
    height += noise(x * freq * 2.0) * 0.08;
    height += noise(x * freq * 3.5) * 0.04;
    return height * (1.0 - layer * 0.3);
}

void main() {
    vec2 coord = uv;
    vec3 color = vec3(0.0);
    
    // Sky gradient
    float t = coord.y;
    color = mix(COLOR_SKY_HORIZON, COLOR_SKY_TOP, smoothstep(0.3, 1.0, t));
    
    // Add stars
    vec2 starCoord = coord * vec2(resolution.x / resolution.y, 1.0) * 20.0;
    float star = hash(floor(starCoord));
    if (star > 0.98) {
        vec2 localPos = fract(starCoord) - 0.5;
        float starDist = length(localPos);
        float starBrightness = (1.0 - smoothstep(0.0, 0.1, starDist)) * smoothstep(0.5, 1.0, coord.y);
        color += vec3(1.0, 0.9, 1.0) * starBrightness * 0.8;
    }
    
    // Draw sun
    vec2 sunPos = vec2(0.5, SUN_Y_POS);
    float sunDist = length(coord - sunPos);
    
    if (sunDist < SUN_SIZE) {
        // Calculate vertical position within sun for gradient
        float sunT = (coord.y - (sunPos.y - SUN_SIZE)) / (SUN_SIZE * 2.0);
        vec3 sunColor;
        if (sunT < 0.5) {
            sunColor = mix(COLOR_SUN_BOTTOM, COLOR_SUN_MID, sunT * 2.0);
        } else {
            sunColor = mix(COLOR_SUN_MID, COLOR_SUN_TOP, (sunT - 0.5) * 2.0);
        }
        
        // Apply sun color with smooth edge
        float sunEdge = 1.0 - smoothstep(SUN_SIZE * 0.95, SUN_SIZE, sunDist);
        color = mix(color, sunColor, sunEdge);
    }
    
    // Sun glow
    if (sunDist < SUN_SIZE * 1.3) {
        float glowIntensity = 1.0 - ((sunDist - SUN_SIZE) / (SUN_SIZE * 0.3));
        glowIntensity = pow(max(glowIntensity, 0.0), 2.0) * 0.4;
        color = mix(color, COLOR_SUN_MID, glowIntensity);
    }
    
    // Horizontal stripes through the sun
    float stripeSpacing = 0.03;
    float stripeWidth = 0.012;
    float stripeY = coord.y - (sunPos.y - SUN_SIZE * 0.5);
    if (sunDist < SUN_SIZE * 1.1 && stripeY > 0.0 && stripeY < SUN_SIZE) {
        float stripeMod = mod(stripeY, stripeSpacing);
        if (stripeMod < stripeWidth) {
            color = mix(color, COLOR_SKY_HORIZON, 0.6);
        }
    }
    
    // Draw wireframe mountains (3 layers for depth)
    for (int layer = 0; layer < 3; layer++) {
        float layerOffset = float(layer) * 0.07;
        float mountainY = HORIZON - 0.05 - layerOffset;
        float mHeight = mountainHeight(coord.x + time * 0.02 * float(layer + 1), float(layer) * 0.3);
        float mountainTop = mountainY + mHeight;
        
        // Draw mountain wireframe
        if (coord.y < mountainTop && coord.y > HORIZON - 0.25) {
            float wireSpacing = 0.04 / (1.0 + float(layer) * 0.5);
            float wireWidth = 0.003;
            
            // Vertical lines
            float xMod = mod(coord.x + time * 0.01 * float(layer + 1), wireSpacing);
            if (xMod < wireWidth) {
                float fadeOut = smoothstep(mountainTop, mountainTop - 0.02, coord.y);
                float layerBrightness = 1.0 - float(layer) * 0.3;
                color = mix(color, COLOR_MOUNTAIN * layerBrightness, fadeOut * 0.7);
            }
            
            // Horizontal lines
            float yDist = abs(coord.y - mountainTop);
            if (yDist < wireWidth) {
                float layerBrightness = 1.0 - float(layer) * 0.3;
                color = mix(color, COLOR_MOUNTAIN * layerBrightness, 0.8);
            }
        }
    }
    
    // Grid floor with perspective (bottom half)
    if (coord.y < HORIZON) {
        // Create perspective effect
        float depth = 1.0 - (coord.y / HORIZON);
        depth = pow(depth, 1.5);
        
        if (depth > 0.01) {
            float perspectiveScale = 1.0 / depth;
            float x = (coord.x - 0.5) * perspectiveScale;
            float z = depth + time * 0.3;
            
            // Grid lines
            float gridX = fract(x / GRID_SIZE);
            float gridZ = fract(z / GRID_SIZE);
            
            float verticalLines = step(1.0 - GRID_LINE_WIDTH * perspectiveScale * 0.5, gridX) + 
                                 step(gridX, GRID_LINE_WIDTH * perspectiveScale * 0.5);
            float horizontalLines = step(1.0 - GRID_LINE_WIDTH, gridZ) + 
                                   step(gridZ, GRID_LINE_WIDTH);
            
            float grid = clamp(verticalLines + horizontalLines, 0.0, 1.0);
            float fadeFactor = 1.0 - pow(depth, 0.5);
            grid *= fadeFactor;
            
            // Blend grid with existing color
            color = mix(color, COLOR_GRID, grid * 0.6);
            
            // Add fog
            float fog = pow(depth, 0.3);
            color = mix(color, COLOR_SKY_HORIZON * 0.2, fog * 0.4);
        }
    }
    
    // Add scan lines for CRT effect
    float scanline = sin(coord.y * resolution.y * 1.5) * 0.5 + 0.5;
    scanline = scanline * 0.05 + 0.95;
    color *= scanline;
    
    // Add slight vignette
    vec2 vignetteCoord = coord * 2.0 - 1.0;
    float vignette = 1.0 - dot(vignetteCoord, vignetteCoord) * 0.3;
    color *= vignette;
    
    fragColor = vec4(color, 1.0);
}
