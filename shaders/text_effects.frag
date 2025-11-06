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

// SDF-based stroke effect
float getStroke(float alpha, float strokeW) {
    // Simple stroke by thickening alpha channel
    float stroke = smoothstep(0.5 - strokeW, 0.5, alpha);
    return stroke;
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
    vec4 finalColor = texColor * v_color;
    
    // Apply gradient if enabled
    if (v_gradient_enabled > 0.5) {
        // Use the V coordinate (vertical) for gradient
        vec4 gradColor = mix(v_gradient_bottom, v_gradient_top, uv.y);
        finalColor.rgb *= gradColor.rgb;
    }
    
    // Apply stroke effect
    if (v_stroke_width > 0.0) {
        float strokeMask = getStroke(texColor.a, v_stroke_width * 0.01);
        float fillMask = texColor.a;
        
        // Blend stroke and fill
        vec4 stroke = vec4(v_stroke_color.rgb, strokeMask);
        finalColor = mix(stroke, finalColor, fillMask);
    }
    
    // Apply shadow effect
    if (length(v_shadow_offset) > 0.0 || v_shadow_blur > 0.0) {
        float shadowMask = getShadow(tex, uv, v_shadow_offset * 0.001, v_shadow_blur * 0.001);
        vec4 shadow = vec4(v_shadow_color.rgb, shadowMask * v_shadow_color.a);
        
        // Blend shadow behind text
        finalColor.rgb = mix(shadow.rgb, finalColor.rgb, finalColor.a);
        finalColor.a = max(finalColor.a, shadow.a);
    }
    
    fragColor = finalColor;
}
