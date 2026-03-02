from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float threshold;
uniform float intensity;
uniform float size;
uniform vec3 color;
uniform float tint;
uniform vec2 RES;

in vec2 v_uv;
out vec4 fragColor;

vec4 glowColor(vec2 Coord, sampler2D Tex, float MipBias) {
    vec2 texelSize = MipBias / RES.xy;

    vec4 result = vec4(0.0);
    result += texture(Tex, Coord, MipBias);
    result += texture(Tex, Coord + vec2(texelSize.x, 0.0), MipBias);
    result += texture(Tex, Coord + vec2(-texelSize.x, 0.0), MipBias);
    result += texture(Tex, Coord + vec2(0.0, texelSize.y), MipBias);
    result += texture(Tex, Coord + vec2(0.0, -texelSize.y), MipBias);
    result += texture(Tex, Coord + vec2(texelSize.x, texelSize.y), MipBias);
    result += texture(Tex, Coord + vec2(-texelSize.x, texelSize.y), MipBias);
    result += texture(Tex, Coord + vec2(texelSize.x, -texelSize.y), MipBias);
    result += texture(Tex, Coord + vec2(-texelSize.x, -texelSize.y), MipBias);

    result /= 9.0;

    // Apply tint after blurring
    vec3 tinted = mix(result.rgb, color, tint);
    return vec4(tinted, result.a);
}



void main() {
    vec2 uv = v_uv;
    vec4 Colorse = texture(Texture, uv);
    vec4 Highlight = clamp(glowColor(uv,Texture,size)-threshold,0.0,1.0)*1.0/(1.0-threshold);
    fragColor = 1.0-(1.0-Colorse)*(1.0-Highlight*intensity); // RES blend
}

"""

def hextocolor(_hex):
    hexcolor = _hex.lstrip("#")
    r = int(hexcolor[0:2],16) / 255.0
    g = int(hexcolor[2:4],16) / 255.0
    b = int(hexcolor[4:6],16) / 255.0

    return (r,g,b)

class Glow:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None): # NOSONAR
        """
        ### Basics:

                # size = min(0) max(10) default(6.)
                size = 6.0,
                # intensity = min(0) max(50) default(1.)
                intensity = 1.0,
                # RES = (w,h)
                RES = (w,h),
                # color = (1.0,1.0,1.0)
                color = (1,1,1),
                # tint = min(0) max(1) default(0.15)
                tint = 0.15,
                # threshold = min(0) max(1) default(.5)
                threshold = 0.5
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
                if prog.name == "intensity":
                    self.prog["intensity"] = float(prog.value)
                if prog.name == "color":
                    self.prog["color"] = hextocolor(prog.value)
                if prog.name == "tint":
                    self.prog["tint"] = float(prog.value)
                if prog.name == "threshold":
                    self.prog["threshold"] = float(prog.value)
            self.prog["RES"] = self.tex.size

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"size","value":"6.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"intensity","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"color","value":"#ffffff","type":sch.TypVar.TYP_VAR_COLOR},
            {"key":"tint","value":"0.15","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"threshold","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"size","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"10"},
            {"key":"intensity","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"50.0"},
            {"key":"color","type":sch.TypVar.TYP_VAR_COLOR,"min":"unl","max":"unl"},
            {"key":"tint","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1."},
            {"key":"threshold","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1."},
        ]
        return data
