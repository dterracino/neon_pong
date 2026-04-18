#version 330

// FTL (Faster Than Light) warp speed background shader
// Original: Dave Hoskins - https://www.shadertoy.com/view/MdKXDm
// Adapted for Neon Pong

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

#define T time * 8.0
#define PI2 6.28318

// Dave Hoskins hash function
// https://www.shadertoy.com/view/4djSRW
float H1(float p) {
    vec3 x = fract(vec3(p) * 0.1031);
    x += dot(x, x.yzx + 19.19);
    return fract((x.x + x.y) * x.z);
}

// IQ cosine palettes
// https://iquilezles.org/articles/palettes
vec3 PT(float t) {
    return vec3(0.5) + vec3(0.5) * cos(6.28318 * (vec3(1.0) * t + vec3(0.0, 0.33, 0.67)));
}

vec3 render(vec3 rd) {
    float a = (atan(rd.y, rd.x) / PI2) + 0.5;  // polar 0-1
    float l = floor(a * 24.0) / 24.0;  // split into 24 segments
    
    // segment colour and edge
    vec3 c = PT(H1(l + T * 0.0001)) * step(0.1, fract(a * 24.0));
    
    // split segments
    float m = mod(abs(rd.y) + H1(l) * 4.0 - T * 0.01, 0.3);
    
    // split segments with brightness
    return c * step(m, 0.16) * m * 16.0 * max(abs(rd.y), 0.0);
}

void main() {
    // Convert UV coordinates to screen space
    vec2 fragCoord = uv * resolution;
    
    // Ray direction
    vec2 screenUv = (fragCoord - resolution * 0.5) / resolution.y;
    vec3 f = vec3(0.0, 0.0, 1.0);
    vec3 r = vec3(f.z, 0.0, -f.x);
    vec3 d = normalize(f + 1.0 * screenUv.x * r + 1.0 * screenUv.y * cross(f, r));
    
    fragColor = vec4(render(d), 1.0);
}