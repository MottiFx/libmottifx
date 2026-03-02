from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform bool INVERT;
uniform float MIX;
uniform vec2 RES;
uniform sampler2D Texture;

in vec2 v_uv;
out vec4 fragColor;

mat3 sobel = mat3(-1, -2, -1,
                   0,  0,  0,
                   1,  2,  1);

vec3 applySobel(sampler2D Tex, vec2 uv) {
    vec2 tex_offset = 1.0 / RES.xy;
    vec3 colX, colY;

    for(int i = 0; i < 3; i++) {
        for(int j = 0; j < 3; j++) {
            vec3 tex = texture(Tex, uv  + vec2(i-1,j-1) * tex_offset).rgb;
            colX += tex * sobel[i][j];
            colY += tex * sobel[j][i];
        }
    }

    return vec3(length(colX.r + colY.r), length(colX.g + colY.g), length(colX.b + colY.b));

}

vec3 applyEdge() {
    vec2 uv = v_uv;
    vec3 edge = applySobel(Texture,uv);

    if(INVERT) {
        edge = vec3(1.0) - edge;
    }

    vec3 orig = texture(Texture, uv).rgb;
    vec3 color = mix (orig,edge,1.0 - MIX);

    return color;
}

void main() {
    fragColor = vec4(applyEdge(), 1.0);
}
"""

class FindEdge:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # mix = min(0.) max(1.) default(0.)
            mix = 0.0
            # invert = True or False default(True)
            invert = True
        """

        if not tex: return

        self.tex = tex
        self.ctx = ctx
        
        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "mix":
                    self.prog["MIX"] = float(prog.value)
                if prog.name == "invert":
                    self.prog["INVERT"] = eval(prog.value)
            self.prog["RES"] = self.tex.size

        
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"mix","value":"0.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"invert","value":"True","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"mix","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1.0"},
            {"key":"invert","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
