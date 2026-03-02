from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float amount;
uniform vec2 resolution;

in vec2 v_uv;
out vec4 fragColor;


vec3 sharpness() {
    vec2 uv = v_uv;
    vec2 pivot = vec2(0.5, 0.5);
    int id = int(dot(vec2(ivec2(pivot) % 2), vec2(1.0, 2.0)));
	vec2 step = vec2((id == 1 || id == 2) ? -1.5 : 1.5, 1.5) / resolution.xy;

    vec3 around = 0.5 * (texture( Texture, uv + step ).rgb + texture( Texture, uv - step ).rgb);

    vec3 center  = texture( Texture, uv ).rgb;

    float sharpen = amount;

    vec3 col = center + (center - around) * sharpen;


    return col;
}

void main() {

    fragColor = vec4(sharpness(),1.0);
}

"""


class Sharpen:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # amount = min(0) max(5) default(1)
            amount = 1.0
        """
        if not tex: return
        
        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "amount":
                    amount = float(prog.value)
                    self.prog["amount"] = amount
            self.prog["resolution"] = self.tex.size

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key": "amount","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"5.0"}
        ]
        return data

