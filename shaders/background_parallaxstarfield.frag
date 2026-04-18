#version 330
// Parallax Starfield Background Shader
// Original by Alexander Lemke, 2015
// Voronoi function based on function from iq
// Simplified as a space background for games by dax105, 2018
// Refactored for Neon Pong by shader-specialist

uniform float time;
uniform vec2 resolution;

in vec2 uv;
out vec4 fragColor;

//#define SHOW_CELLS
//#define USE_VORONOI
#define STAR_LAYER_COUNT 10

vec2 hash(in vec2 p) {
	return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);
}

vec2 hash22(vec2 p)
{
	vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yzx+19.19);
    return fract((p3.xx+p3.yz)*p3.zy);
}

float noise(in vec2 p) {
    #ifdef USE_VORONOI
    
    vec2 n = floor(p);
    vec2 f = fract(p);

    vec2 mg, mr;

    float md = 8.0;
    for(int j = -1; j <= 1; ++j) {
        for(int i = -1; i <= 1; ++i) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = hash22(n + g);

            vec2 r = g + o - f;
            float d = dot(r, r);

            if(d < md) {
                md = d;
                mr = r;
                mg = g;
            }
        }
    }
    return md;
    
    #else
    
    vec2 n = floor(p);
    vec2 f = fract(p);

    float md = 1.0;

    // Scale a bit to move from cell edges
    vec2 o = hash22(n)*0.96 + 0.02;

    vec2 r = o - f;
    float d = dot(r, r);

    md = min(d, md);

    return md;
    
    #endif
}

vec3 starfield(vec2 samplePosition, float threshold) {
    float starValue = noise(samplePosition);
    
    float power = max(1.0 - (starValue / threshold), 0.0);
    power = power * power * power;
    
    #ifdef SHOW_CELLS
    power += starValue;
    #endif
    
    return vec3(power);
}

void main() {
    // Convert UV coordinates to fragment coordinates compatible with original shader
    vec2 fragCoord = uv * resolution;
    float maxResolution = max(resolution.x, resolution.y);
    
	vec3 finalColor = vec3(0.0);
    vec2 sCoord = (fragCoord.xy / maxResolution) * 5.0;
    vec2 pos = vec2(time * 5.0, sin(time) * 5.0);
    
    // Add starfields - multiple layers with parallax effect
    for (int i = 1; i <= STAR_LAYER_COUNT; i++) {
        float fi = float(i);
        float inv = sqrt(1.0 / fi);
    	finalColor += starfield((sCoord + vec2(fi * 100.0, -fi * 50.0)) * (1.0 + fi * 0.2) + pos, 0.0005) * inv;
    }
    
    fragColor = vec4(finalColor, 1.0);
}
