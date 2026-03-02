from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

#define PI 3.14159
uniform float angle;
uniform float radius;
uniform vec2 center;
uniform vec2 RES;
uniform sampler2D Texture;

in vec2 v_uv;
out vec4 fragColor;


vec4 swirl() {
    vec2 centerM = center.xy ;
    vec2 uv = v_uv - centerM;
    float angleS = angle * PI;

    float len = length(uv * vec2(RES.x / RES.y,1.));
    float ANGLEEFFECT = atan(uv.y, uv.x) + angleS * smoothstep(radius,0.,len);
    float RADIUSEFFECT = length(uv);

    vec4 swirlMe = texture(Texture, vec2(RADIUSEFFECT*cos(ANGLEEFFECT), RADIUSEFFECT * sin(ANGLEEFFECT)) + centerM);

    return swirlMe;
}


void main(){
    fragColor = swirl();
}
"""

class Swirl:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
            ### Basics:
            center = (0.5,0.5)
            # angle = min(0.) max(unlimited) default(1.0)
            angle = 1.0
            # radius = min(0.) max(unlimited) default(0.5)
            radius = 0.5
        """

        if not tex: return

        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "angle":
                    angle = float(prog.value)
                    self.prog["angle"] = angle
                if prog.name == "radius":
                    radius = float(prog.value)
                    self.prog["radius"] = radius
                if prog.name == "center":
                    center = eval(prog.value)
                    self.prog["center"] = center
            self.prog["RES"] = self.tex.size

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"angle","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"radius","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"angle","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
            {"key":"radius","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
            {"key":"center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
        ]
        return data
