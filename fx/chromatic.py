from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
    #version 450

    uniform sampler2D Texture;
    uniform float strength;

    in vec2 v_uv;
    out vec4 fragColor;

    vec3 chromatic() {
        vec2 uv = v_uv;
        float offset = strength / 100;
        vec3 texColor;
        texColor.r = texture(Texture, uv + vec2(offset, 0.0)).r;
        texColor.g = texture(Texture, uv).g;
        texColor.b = texture(Texture, uv - vec2(offset, 0.0)).b;
        vec3 group = vec3(texColor.r,texColor.g,texColor.b);

        return group;
    }
    void main() {
        fragColor = vec4(chromatic(), 1.0);
    }
"""


class Chromatic:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Example:

            # strength = min(0) max(unlimited) default(.3)
            strength = 0.3
        """
        if not tex: return
        
        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "strength":
                    strength = float(prog.value)
                    self.prog["strength"] = strength
            self.prog["Texture"] = 0
        

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"strength","value":"0.3","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"strength","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"}
        ]
        return data
