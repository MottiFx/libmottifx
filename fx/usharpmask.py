from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float amount;
uniform float radius;
uniform bool preserveAlpha;

in vec2 v_uv;
out vec4 fragColor;


vec4 unsharpmask(){
    vec2 uv = v_uv;
    vec4 original = texture(Texture,uv);
    vec4 alpha = texture(Texture,uv,radius);

    // mask
    alpha = original  - alpha;
    original += alpha * amount;

    float validated = float(preserveAlpha);

    return mix(original,alpha,validated);
}


void main() {
    fragColor = unsharpmask();
}

"""

class UsharpMask:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # amount = min(0) max(unlimited) default(.5)
            amount = 0.5
            # radius = min(0) max(unlimited) default(6.)
            radius = 6.0
            # alpha = True Or False default(False)
            alpha = False
        """

        if not tex: return

        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "amount":
                    self.prog["amount"] = float(prog.value)
                if prog.name == "radius":
                    self.prog["radius"] = float(prog.value)
                if prog.name == "alpha":
                    self.prog["preserveAlpha"] = eval(prog.value)
    
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"amount","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"radius","value":"6.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"alpha","value":"False","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"radius","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"alpha","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
