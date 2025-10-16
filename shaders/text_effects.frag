#version 330

uniform sampler2D tex;
uniform vec4 color;

// Text effects uniforms
uniform float strokeWidth;
uniform vec4 strokeColor;
uniform vec2 shadowOffset;
uniform float shadowBlur;
uniform vec4 shadowColor;
uniform bool gradientEnabled;
uniform vec4 gradientColorTop;
uniform vec4 gradientColorBottom;

in vec2 uv;
in vec2 fragPos;  // Fragment position in texture coordinates for gradient
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
    vec4 finalColor = texColor * color;
    
    // Apply gradient if enabled
    if (gradientEnabled) {
        // Use the V coordinate (vertical) for gradient
        vec4 gradColor = mix(gradientColorBottom, gradientColorTop, uv.y);
        finalColor.rgb *= gradColor.rgb;
    }
    
    // Apply stroke effect
    if (strokeWidth > 0.0) {
        float strokeMask = getStroke(texColor.a, strokeWidth * 0.01);
        float fillMask = texColor.a;
        
        // Blend stroke and fill
        vec4 stroke = vec4(strokeColor.rgb, strokeMask);
        finalColor = mix(stroke, finalColor, fillMask);
    }
    
    // Apply shadow effect (rendered in a separate pass would be better, but this works)
    if (length(shadowOffset) > 0.0 || shadowBlur > 0.0) {
        float shadowMask = getShadow(tex, uv, shadowOffset * 0.001, shadowBlur * 0.001);
        vec4 shadow = vec4(shadowColor.rgb, shadowMask * shadowColor.a);
        
        // Blend shadow behind text
        finalColor.rgb = mix(shadow.rgb, finalColor.rgb, finalColor.a);
        finalColor.a = max(finalColor.a, shadow.a);
    }
    
    fragColor = finalColor;
}
