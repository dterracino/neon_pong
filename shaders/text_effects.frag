#version 330

uniform sampler2D tex;

// Effect parameters from vertex shader (interpolated per-fragment)
in vec2 uv;
in vec2 fragPos;
in vec4 v_color;
in float v_stroke_width;
in vec4 v_stroke_color;
in vec2 v_shadow_offset;
in float v_shadow_blur;
in vec4 v_shadow_color;
in float v_gradient_enabled;
in vec4 v_gradient_top;
in vec4 v_gradient_bottom;

out vec4 fragColor;

// Stroke effect by sampling surrounding pixels
float getStroke(sampler2D tex, vec2 uv, vec2 texelSize, float strokeW) {
    if (strokeW <= 0.0) {
        return 0.0;
    }
    
    // Sample surrounding pixels to create outline
    float maxAlpha = 0.0;
    int samples = 12;
    float radius = strokeW;  // Stroke width in pixels
    
    for (int i = 0; i < samples; i++) {
        float angle = 3.14159265 * 2.0 * float(i) / float(samples);
        vec2 offset = vec2(cos(angle), sin(angle)) * radius * texelSize;
        float sampleAlpha = texture(tex, uv + offset).a;
        maxAlpha = max(maxAlpha, sampleAlpha);
    }
    
    return maxAlpha;
}

// Soft shadow effect using multiple samples
float getShadow(sampler2D tex, vec2 uv, vec2 offset, float blur) {
    if (blur <= 0.0) {
        return texture(tex, uv + offset).a;
    }
    
    // Simple box blur for shadow
    float shadow = 0.0;
    int samples = 4;
    float step = blur / float(samples);
    
    for (int x = -samples; x <= samples; x++) {
        for (int y = -samples; y <= samples; y++) {
            vec2 sampleOffset = offset + vec2(float(x), float(y)) * step;
            shadow += texture(tex, uv + sampleOffset).a;
        }
    }
    
    shadow /= float((samples * 2 + 1) * (samples * 2 + 1));
    return shadow;
}

void main() {
    vec4 texColor = texture(tex, uv);
    
    // Calculate texel size for proper stroke sampling
    vec2 texelSize = 1.0 / vec2(textureSize(tex, 0));
    
    // Apply gradient if enabled (to the base text color)
    vec4 finalColor = texColor * v_color;
    if (v_gradient_enabled > 0.5) {
        vec4 gradColor = mix(v_gradient_bottom, v_gradient_top, uv.y);
        finalColor.rgb *= gradColor.rgb;
    }
    
    // Apply stroke effect
    if (v_stroke_width > 0.0) {
        // Get stroke mask by sampling surrounding area
        float strokeMask = getStroke(tex, uv, texelSize, v_stroke_width);
        
        // Create stroke layer (background)
        vec4 strokeLayer = vec4(v_stroke_color.rgb, strokeMask * v_stroke_color.a);
        
        // Blend text on top of stroke
        fragColor = mix(strokeLayer, finalColor, texColor.a);
    } else {
        // No stroke, just use the text color
        fragColor = finalColor;
    }
    
    // Apply shadow effect (only if no stroke, to keep it simple for now)
    if (v_stroke_width <= 0.0 && (length(v_shadow_offset) > 0.0 || v_shadow_blur > 0.0)) {
        float shadowMask = getShadow(tex, uv, v_shadow_offset * 0.001, v_shadow_blur * 0.001);
        vec4 shadow = vec4(v_shadow_color.rgb, shadowMask * v_shadow_color.a);
        
        // Blend shadow behind text
        fragColor.rgb = mix(shadow.rgb, fragColor.rgb, fragColor.a);
        fragColor.a = max(fragColor.a, shadow.a);
    }
}
