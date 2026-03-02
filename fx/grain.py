import time
from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch
from guimottifx.utils.configediting import ConfigTimeLine

fragment_shader = """
#version 450

uniform float scale;
uniform float amount;
uniform bool TRGB;
uniform sampler2D Texture;
uniform vec2 RES;
uniform float iTime;

in vec2 v_uv;
out vec4 fragColor;

float rand(vec2 co, float time) {
    return fract(sin(dot(co.xy, vec2(12.9898,78.233))) * 43758.5453 + time);
}

vec4 grain() {
    vec2 ps = vec2(1.0) / RES.xy;
    vec2 uv = v_uv;

    vec4 oriTex = texture(Texture, uv);

    if (TRGB) {
        float r = texture(Texture, uv + (rand(uv + vec2(1.0, 0.0), iTime) - 0.5) * 2.0 * ps * scale).r;
        float g = texture(Texture, uv + (rand(uv + vec2(0.0, 1.0), iTime + 10.0) - 0.5) * 2.0 * ps * scale).g;
        float b = texture(Texture, uv + (rand(uv + vec2(1.0, 1.0), iTime + 20.0) - 0.5) * 2.0 * ps * scale).b;

        vec3 noiseColor = vec3(r, g, b);
        oriTex.rgb = mix(oriTex.rgb, noiseColor, amount);
    }
    else {
        vec2 offset = (rand(uv, iTime) - 0.5) * 2.0 * ps * scale;
        vec3 noise = texture(Texture, uv + offset).rgb;
        oriTex.rgb = mix(oriTex.rgb, noise, amount);
    }

    return oriTex;
}

void main() {
    fragColor = grain();
}


""" 
class Grain:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # RES = (w,h)
            RES = (w,h)
            # scale = min(0) max(unlimited) default(20.)
            scale = 20.0
            # amount = min(0) max(1) default(.5)
            amount = 0.5
            # trgb = True or False default(false)
            trgb = False
            # iTime = time video yang tersedia saja
            iTime = time.time_ns()
        """

        if not tex: return

        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "scale": self.prog["scale"] = float(prog.value)
                if prog.name == "amount": self.prog["amount"] = float(prog.value)
                if prog.name == "trgb": self.prog["TRGB"] = eval(prog.value)
            self.prog["iTime"] = itime
            self.prog["RES"] = self.tex.size

        
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"scale","value":"10.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"amount","value":".5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"trgb","value":"True","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"scale","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key":"trgb","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
