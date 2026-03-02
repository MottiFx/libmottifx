from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float range;
uniform float steps;
uniform float threshold;
uniform float brightness;
uniform vec3 color;
uniform float tint;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec2 uv = v_uv;
    fragColor = texture(Texture, uv);

    for (float i = -range; i < range; i += steps) {
        float falloff = 1.0 - abs(i / range);

        vec4 blurr = texture(Texture, uv + i);

        // after
        float lum = blurr.r + blurr.g + blurr.b;
        float ifglow = step(threshold * 3.0, lum);

        // karena ifglow itu menghasilkan 0.0 = False dan 1.0 = True, jadi bisa langsung dikali saja karena menggunakan mix juga, kalau False hasilnya bakal 0 semua karena 0.0 = False

        fragColor.rgb += mix(blurr.rgb,color,tint) * falloff * steps * brightness * ifglow;

        blurr = texture(Texture, uv + vec2(i, -i));

        lum = blurr.r + blurr.g + blurr.b;
        ifglow = step(threshold * 3.0, lum);

        fragColor.rgb += mix(blurr.rgb,color,tint) * falloff * steps * brightness * ifglow; 

        // before
        /* if (blurr.r + blurr.g + blurr.b > threshold * 3.0) {
            fragColor.rgb += mix(blurr.rgb,color,tint) * falloff * steps * brightness;
        }
        
        blurr = texture(Texture, uv + vec2(i, -i));
        if (blurr.r + blurr.g + blurr.b > threshold * 3.0) {
            fragColor.rgb += mix(blurr.rgb,color,tint) * falloff * steps * brightness;
        }
        */
    }

}
"""

def hextocolor(_hex):
    hexcolor = _hex.lstrip("#")
    r = int(hexcolor[0:2],16) / 255.0
    g = int(hexcolor[2:4],16) / 255.0
    b = int(hexcolor[4:6],16) / 255.0

    return (r,g,b)

class StarGlow:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # range = min(0) max(1) default(0.3)
            range = 0.3
            # steps = min(0.001) max(0.01) default(0.001)
            steps = 0.001
            # threshold = min(0) max(1) default(0.7)
            threshold = 0.7
            # brightness = min(0) max(5) default(1.5)
            brightness = 1.5
            # tint = min(0) max(1) default(1.)
            tint = 1.0
            # color = min(0.) max(1.) default(0, 1, 1) change color
            color = (0.,1.,1.)
        """

        if not tex: return

        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name in ["range","steps","threshold","brightness","tint"]:
                    namevar = prog.name
                    val = float(prog.value)
                    self.prog[namevar] = val
                if prog.name == "color":
                    color = hextocolor(prog.value)
                    self.prog["color"] = color

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data  = [
            {"key":"range","value":"0.3","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"steps","value":"0.001","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"threshold","value":"0.7","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"brightness","value":"1.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"tint","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"color","value":"#ff7777","type":sch.TypVar.TYP_VAR_COLOR},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"range","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"0.3"},
            {"key":"steps","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.001","max":"0.01"},
            {"key":"threshold","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1.0"},
            {"key":"brightness","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"5."},
            {"key":"tint","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1."},
            {"key":"color","type":sch.TypVar.TYP_VAR_COLOR,"min":"0.","max":"1."},
        ]

        return data
