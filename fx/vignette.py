from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450
uniform sampler2D Texture;
uniform vec2 center;
uniform float amount;
uniform float size;

in vec2 v_uv;
out vec4 f_color;

void main() {
    vec2 uv = v_uv;
    vec2 delta = v_uv - center;
    float dist = length(delta);
    float vignette = smoothstep(size, size + amount, dist);
    vec3 color = texture(Texture, uv).rgb;
    color *= 1.0 - vignette;
    f_color = vec4(color, 1.0);
}
"""


class Vignette:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            center = (0.5,0.5)
            # amount = min(0) max(1) default(.35)
            amount = 0.35
            # size = min(0) max(1) default(0.1)
            size = 0.1
        """

        if not tex: return

        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "center":
                    self.prog["center"] = eval(prog.value)
                if prog.name == "amount":
                    self.prog["amount"] = float(prog.value)
                if prog.name == "size":
                    self.prog["size"] = float(prog.value)

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key":"amount","value":"0.35","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"size","value":"0.1","type":sch.TypVar.TYP_VAR_FLOAT},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key":"size","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
        ]
        return data
