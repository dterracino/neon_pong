#version 330

// Vertex position and texture coordinates
in vec2 in_position;
in vec2 in_uv;

// Per-vertex effect parameters (same for all 6 vertices of a quad)
in vec4 in_color;
in float in_stroke_width;
in vec4 in_stroke_color;
in vec2 in_shadow_offset;
in float in_shadow_blur;
in vec4 in_shadow_color;
in float in_gradient_enabled;
in vec4 in_gradient_top;
in vec4 in_gradient_bottom;

// Outputs to fragment shader
out vec2 uv;
out vec2 fragPos;
out vec4 v_color;
out float v_stroke_width;
out vec4 v_stroke_color;
out vec2 v_shadow_offset;
out float v_shadow_blur;
out vec4 v_shadow_color;
out float v_gradient_enabled;
out vec4 v_gradient_top;
out vec4 v_gradient_bottom;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    uv = in_uv;
    fragPos = in_uv;
    
    // Pass effect parameters to fragment shader
    v_color = in_color;
    v_stroke_width = in_stroke_width;
    v_stroke_color = in_stroke_color;
    v_shadow_offset = in_shadow_offset;
    v_shadow_blur = in_shadow_blur;
    v_shadow_color = in_shadow_color;
    v_gradient_enabled = in_gradient_enabled;
    v_gradient_top = in_gradient_top;
    v_gradient_bottom = in_gradient_bottom;
}
