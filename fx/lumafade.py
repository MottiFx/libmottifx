from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float interpolation;
uniform float intensity;

in vec2 v_uv;
out vec4 fragColor;

const vec4 colorClear = vec4(0.,0.,0.,0.);
const vec4 colorBlack = vec4(0.,0.,0.,1.);

void main() {
    vec2 texUv = v_uv;
    vec4 texColor = texture(Texture, texUv);

    float itpCosine = cos(interpolation);
    float cosSquared = itpCosine * itpCosine;

    float fadeStrength = smoothstep(0.01,0.1,interpolation);
    
    // apply fade strength
    float brightness = length(mix(texColor,colorClear,cosSquared * fadeStrength));
    float alphaFactor = pow(brightness, intensity);

    fragColor = vec4(texColor.rgb * clamp(alphaFactor,0.,1.),1.0);
}
"""


class LumaFade:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # interpolation = min(0) max(1.) default(0.5)
            interpolation = 0.5
            # intensity = min(unlimited) max(unlimited) default(10.)
            intensity = 10.0
        """

        if not tex: return
        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "interpolation":
                    polation = float(prog.value)
                    self.prog["interpolation"] = polation
                elif prog.name == "intensity":
                    tensity = float(prog.value)
                    self.prog["intensity"] = tensity
            self.prog["Texture"] = 0


    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"interpolation","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"intensity","value":"10.0","type":sch.TypVar.TYP_VAR_MINUS},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"interpolation","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"1.0"},
            {"key":"intensity","type":sch.TypVar.TYP_VAR_MINUS,"min":"unl","max":"unl"},
        ]
        return data
