#version 330 // specify we are indeed using modern opengl

uniform sampler2DArray texture_array_sampler;

out vec4 fragment_colour; // output of our shader

in vec3 local_position;  // interpolated vertex position
in vec3 interpolated_tex_coords;
in float interpolated_shading_value;

void main(void) {
	vec4 texture_color = texture(texture_array_sampler, interpolated_tex_coords);
	fragment_colour = texture_color * interpolated_shading_value;

	if (texture_color.a == 0.0) {
		discard;
	}
}