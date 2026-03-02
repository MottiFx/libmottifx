from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform vec2 RES;
uniform float highlight;
uniform int samples;
uniform float radius;
uniform float size;
uniform sampler2D Texture;
#define GoldenAngle 2.399996 // rad


in vec2 v_uv;
out vec4 fragColor;

mat2 rot(float a) {
    float c = cos(a);
    float s = sin(a);
    return mat2(c, s, -s, c);
}

vec3 bokeh() {
    vec2 uv = v_uv;
    vec3 total = vec3(0.);
    vec3 divsor = vec3(0.);
    float r = 1.;
    mat2 G = rot(GoldenAngle);

    float rd = RES.x * radius;
    rd += fract(radius * .1) * radius;
    rd = mod(rd,radius);

    vec2 offset = vec2(rd, 0.);

    for(int i = 0; i < samples; i++) {
        r += 1./r;
        offset = G * offset;
        vec3 col = texture(Texture, uv + offset * (r - 1.) * size / RES.xy).rgb;
        vec3 bokeh = pow(col,vec3(highlight));
        total += col * bokeh;
        divsor += bokeh;
    }

    return total / divsor;

}


void main() {
    fragColor = vec4(bokeh(),1.0);
}

"""

class Bokeh:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None): #NOSONAR
        """
        ### Example:
            
            # size = min(0) max(unlimited) default(1.)
            size = 1.0
            # radius = min(0.1) max(9) default(5.)
            radius = 5.0
            # samples = min(0) max(unlimited) default(64)
            samples = 64
            # highlight = min(0) max(unlimited) default(4.)
            highlight = 4.0
        
        """

        if not tex: return
        
        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "size":
                    self.prog["size"] = float(prog.value)
                if prog.name == "radius":
                    self.prog["radius"] = float(prog.value)
                if prog.name == "samples":
                    self.prog["samples"] = int(prog.value)
                if prog.name == "highlight":
                    self.prog["highlight"] = float(prog.value)
            self.prog["RES"] = self.tex.size
        
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"size","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"radius","value":"5.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"samples","value":"64","type":sch.TypVar.TYP_VAR_INT},
            {"key":"highlight","value":"4.0","type":sch.TypVar.TYP_VAR_FLOAT},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"size","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
            {"key":"radius","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.1","max":"9.0"},
            {"key":"samples","type":sch.TypVar.TYP_VAR_INT,"min":"0","max":"unl"},
            {"key":"highlight","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
        ]
        return data
