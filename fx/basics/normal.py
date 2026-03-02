

fragment_shader = """
#version 450

uniform sampler2D Texture;
in vec2 v_uv;
out vec4 f_color;
void main() {
    f_color = texture(Texture,v_uv);
}
"""

class BasicShader:
    def __init__(self,tex,ctx,vertex_shader,vbo):
        self.tex= tex
        self.ctx= ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()