#version 330
// Retro/Synthwave Background Shader
// Based on classic 80s synthwave aesthetic
// Large striped sun, wireframe mountains, perspective grid

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Color palette - classic synthwave
const vec3 COLOR_SKY_TOP = vec3(0.02, 0.0, 0.15);          // Very dark blue
const vec3 COLOR_SKY_HORIZON = vec3(0.2, 0.05, 0.3);       // Dark purple
const vec3 COLOR_SUN_TOP = vec3(1.0, 0.95, 0.2);           // Bright yellow
const vec3 COLOR_SUN_BOTTOM = vec3(1.0, 0.3, 0.4);         // Pink/coral
const vec3 COLOR_GRID = vec3(1.0, 0.1, 0.5);               // Hot pink/magenta
const vec3 COLOR_MOUNTAIN = vec3(0.0, 0.0, 0.0);           // Black (silhouette)
const vec3 COLOR_MOUNTAIN_WIRE = vec3(0.0, 0.6, 0.8);      // Cyan for wireframe

const float HORIZON = 0.48;
const float SUN_Y = 0.48;  // Sun sits right on horizon
const float SUN_RADIUS = 0.25;
const float GRID_SIZE = 0.05;

// Simple hash for randomness
float hash(float n) {
    return fract(sin(n) * 43758.5453123);
}

// 2D hash
float hash2(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

// Simple mountain height function
float mountainHeight(float x, float seed) {
    float h = 0.0;
    // Use multiple octaves for more interesting shapes
    h += sin(x * 2.0 + seed * 10.0) * 0.08;
    h += sin(x * 4.0 + seed * 15.0) * 0.04;
    h += sin(x * 8.0 + seed * 20.0) * 0.02;
    return h;
}

void main() {
    vec2 coord = uv;
    vec3 color = vec3(0.0);
    
    // Sky gradient - darker at top, lighter purple at horizon
    float skyGradient = smoothstep(HORIZON, 1.0, coord.y);
    color = mix(COLOR_SKY_HORIZON, COLOR_SKY_TOP, skyGradient);
    
    // Add stars in the upper sky
    if (coord.y > HORIZON + 0.1) {
        vec2 starCoord = coord * vec2(resolution.x / resolution.y, 1.0) * 30.0;
        float star = hash2(floor(starCoord));
        if (star > 0.985) {
            vec2 localPos = fract(starCoord) - 0.5;
            float starDist = length(localPos);
            float starIntensity = (1.0 - smoothstep(0.0, 0.08, starDist)) * (coord.y - HORIZON - 0.1);
            color += vec3(1.0, 0.95, 1.0) * starIntensity * 0.6;
        }
    }
    
    // Draw the sun - large circle at horizon with horizontal stripes
    vec2 sunPos = vec2(0.5, SUN_Y);
    float sunDist = length(coord - sunPos);
    
    // Only draw bottom half of sun (it's "setting")
    if (sunDist < SUN_RADIUS && coord.y < SUN_Y) {
        // Gradient from yellow at top to pink at bottom
        float sunGrad = (coord.y - (SUN_Y - SUN_RADIUS)) / (SUN_RADIUS * 2.0);
        vec3 sunColor = mix(COLOR_SUN_BOTTOM, COLOR_SUN_TOP, sunGrad);
        
        // Smooth edge
        float edge = 1.0 - smoothstep(SUN_RADIUS * 0.97, SUN_RADIUS, sunDist);
        color = mix(color, sunColor, edge);
        
        // Add horizontal stripes through the sun
        float stripeSpacing = 0.025;
        float stripeY = coord.y - SUN_Y;
        float stripeMod = mod(abs(stripeY), stripeSpacing);
        if (stripeMod < stripeSpacing * 0.35) {
            // Dark stripe
            color = mix(color, COLOR_SKY_HORIZON * 0.4, edge * 0.7);
        }
    }
    
    // Draw wireframe mountains - triangular peaks in the mid-ground
    // We'll draw 3-4 layers for depth
    for (int layer = 0; layer < 3; layer++) {
        float layerDepth = float(layer) * 0.08;
        float baseY = HORIZON - 0.15 - layerDepth;
        
        // Sample mountain height at this x position
        float mHeight = mountainHeight(coord.x * 3.0 + float(layer) * 1.5 + time * 0.01, float(layer));
        float mountainTop = baseY + mHeight;
        
        // Check if we're inside the mountain region
        if (coord.y < mountainTop && coord.y > baseY - 0.2) {
            // Solid fill for mountains
            if (coord.y < mountainTop) {
                color = COLOR_MOUNTAIN;
            }
            
            // Wireframe overlay
            float wireSpacing = 0.03;
            float wireThickness = 0.002;
            
            // Vertical wires
            float xMod = mod(coord.x + float(layer) * 0.1 + time * 0.005, wireSpacing);
            if (xMod < wireThickness || xMod > wireSpacing - wireThickness) {
                if (coord.y < mountainTop) {
                    float wireFade = smoothstep(mountainTop - 0.01, mountainTop, coord.y);
                    color = mix(COLOR_MOUNTAIN_WIRE, color, wireFade);
                }
            }
            
            // Horizontal wire at peak
            if (abs(coord.y - mountainTop) < wireThickness * 2.0) {
                color = COLOR_MOUNTAIN_WIRE;
            }
        }
    }
    
    // Perspective grid floor
    if (coord.y < HORIZON) {
        // Calculate depth/perspective
        float depth = (HORIZON - coord.y) / HORIZON;
        depth = pow(depth, 1.2);
        
        if (depth > 0.01) {
            // Perspective-corrected coordinates
            float perspectiveScale = 1.0 / depth;
            float x = (coord.x - 0.5) * perspectiveScale;
            float z = depth * 2.0 + time * 0.2;  // Moving forward
            
            // Grid pattern
            float gridX = fract(x / GRID_SIZE);
            float gridZ = fract(z / GRID_SIZE);
            
            float lineThickness = 0.02;
            
            // Vertical lines (going into distance)
            bool verticalLine = gridX < lineThickness * perspectiveScale * 0.5 || 
                               gridX > 1.0 - lineThickness * perspectiveScale * 0.5;
            
            // Horizontal lines (perpendicular to view)
            bool horizontalLine = gridZ < lineThickness || gridZ > 1.0 - lineThickness;
            
            if (verticalLine || horizontalLine) {
                // Fade grid with distance
                float fadeFactor = 1.0 - pow(depth, 0.4);
                color = mix(color, COLOR_GRID, fadeFactor * 0.8);
            }
        }
    }
    
    // Subtle vignette
    vec2 vignetteCoord = coord * 2.0 - 1.0;
    float vignette = 1.0 - dot(vignetteCoord, vignetteCoord) * 0.2;
    color *= vignette;
    
    // Scan lines for CRT effect
    float scanline = sin(coord.y * resolution.y * 2.0) * 0.5 + 0.5;
    scanline = scanline * 0.04 + 0.96;
    color *= scanline;
    
    fragColor = vec4(color, 1.0);
}
