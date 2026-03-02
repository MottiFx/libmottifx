from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform bool flip_x;
uniform bool flip_y;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec2 uv = v_uv;
    uv.x = flip_x ? 1.0 - uv.x : uv.x;
    uv.y = !flip_y ? 1.0 - uv.y : uv.y;
    fragColor = texture(Texture, uv);

}
"""

class Flip:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # vertical = only 1.0 || 0.0 default(0)
            vertical = 0
            # horizontal = only 1.0 || 0.0 default(0)
            horizontal = 0
        """

        if not tex: return
        
        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                self.prog[prog.name] = eval(prog.value)
        
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"flip_x","value":"True","type":sch.TypVar.TYP_VAR_BOOL},
            {"key":"flip_y","value":"True","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data

    def get_type(self):
        data = [
            {"key":"flip_x","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
            {"key":"flip_y","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
