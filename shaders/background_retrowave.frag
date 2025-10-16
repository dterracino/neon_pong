#version 330
// Retrowave Background Shader
// Creates a classic retrowave/synthwave aesthetic with:
// - Perspective grid floor
// - Gradient sky (dark purple to pink)
// - Animated sun on the horizon
// - Scan lines for CRT effect

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

// Constants for retrowave look
const vec3 COLOR_SKY_TOP = vec3(0.05, 0.02, 0.15);      // Dark purple
const vec3 COLOR_SKY_HORIZON = vec3(0.4, 0.15, 0.5);    // Purple
const vec3 COLOR_SUN = vec3(1.0, 0.44, 0.81);           // Neon pink
const vec3 COLOR_GRID = vec3(0.0, 0.8, 0.996);          // Cyan
const vec3 COLOR_FLOOR = vec3(0.02, 0.01, 0.08);        // Very dark purple

const float HORIZON = 0.45;  // Horizon line position (0-1)
const float GRID_SIZE = 0.1; // Grid cell size
const float GRID_LINE_WIDTH = 0.02;
const float SUN_SIZE = 0.15;
const float SUN_GLOW = 0.3;

void main() {
    vec2 coord = uv;
    vec3 color = vec3(0.0);
    
    // Sky gradient (top half)
    if (coord.y > HORIZON) {
        float t = (coord.y - HORIZON) / (1.0 - HORIZON);
        color = mix(COLOR_SKY_HORIZON, COLOR_SKY_TOP, t);
        
        // Add sun on horizon
        vec2 sunPos = vec2(0.5, HORIZON + 0.05);
        float sunDist = length(coord - sunPos);
        
        // Sun core
        if (sunDist < SUN_SIZE) {
            float sunIntensity = 1.0 - (sunDist / SUN_SIZE);
            sunIntensity = pow(sunIntensity, 2.0);
            color = mix(color, COLOR_SUN, sunIntensity);
        }
        
        // Sun glow
        if (sunDist < SUN_SIZE + SUN_GLOW) {
            float glowIntensity = 1.0 - ((sunDist - SUN_SIZE) / SUN_GLOW);
            glowIntensity = pow(glowIntensity, 3.0) * 0.6;
            color = mix(color, COLOR_SUN, glowIntensity);
        }
        
        // Horizontal sun stripes for that retro look
        float stripeCount = 8.0;
        float stripeY = coord.y - sunPos.y;
        if (abs(stripeY) < SUN_SIZE) {
            float stripe = sin(stripeY * 3.14159 * stripeCount) * 0.5 + 0.5;
            stripe = step(0.7, stripe);
            color = mix(color, COLOR_SKY_HORIZON, stripe * 0.3);
        }
    }
    // Grid floor with perspective (bottom half)
    else {
        color = COLOR_FLOOR;
        
        // Create perspective effect
        // Map Y coordinate to depth (closer = bottom of screen)
        float depth = 1.0 - (coord.y / HORIZON);
        depth = pow(depth, 1.5); // Non-linear perspective
        
        // Prevent division by zero and extreme values
        if (depth > 0.01) {
            // Calculate perspective-corrected coordinates
            float perspectiveScale = 1.0 / depth;
            
            // X position with perspective (centered)
            float x = (coord.x - 0.5) * perspectiveScale;
            
            // Z position (depth into screen) - animated moving forward
            float z = depth + time * 0.3;
            
            // Grid lines
            float gridX = fract(x / GRID_SIZE);
            float gridZ = fract(z / GRID_SIZE);
            
            // Draw vertical grid lines (going into distance)
            float verticalLines = step(1.0 - GRID_LINE_WIDTH * perspectiveScale * 0.5, gridX) + 
                                 step(gridX, GRID_LINE_WIDTH * perspectiveScale * 0.5);
            
            // Draw horizontal grid lines (perpendicular to view)
            float horizontalLines = step(1.0 - GRID_LINE_WIDTH, gridZ) + 
                                   step(gridZ, GRID_LINE_WIDTH);
            
            // Combine grid lines
            float grid = clamp(verticalLines + horizontalLines, 0.0, 1.0);
            
            // Fade grid lines with distance
            float fadeFactor = 1.0 - pow(depth, 0.5);
            grid *= fadeFactor;
            
            // Apply grid color
            color = mix(color, COLOR_GRID, grid * 0.8);
            
            // Add subtle fog/fade towards horizon
            float fog = pow(depth, 0.3);
            color = mix(color, COLOR_SKY_HORIZON * 0.3, fog * 0.5);
        }
    }
    
    // Add scan lines for CRT effect
    float scanline = sin(coord.y * resolution.y * 1.5) * 0.5 + 0.5;
    scanline = scanline * 0.05 + 0.95; // Subtle effect
    color *= scanline;
    
    // Add slight vignette
    vec2 vignetteCoord = coord * 2.0 - 1.0;
    float vignette = 1.0 - dot(vignetteCoord, vignetteCoord) * 0.3;
    color *= vignette;
    
    fragColor = vec4(color, 1.0);
}
