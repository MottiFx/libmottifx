from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

uniform int Samples;
uniform float Strength;
uniform vec2 center;
uniform sampler2D Texture;


in vec2 v_uv;
out vec4 fragColor;


vec3 radialblur(){
    vec2 uv = v_uv;

    vec2 diff = uv - center;
    vec4 col = vec4(0.); 

    float fSamples = float(Samples);
    float sampleSize = 1. / fSamples;

    for (int i = 0; i < Samples; i++){
        float fac = float(i) * sampleSize;
        vec2 pos = uv - diff * (fac * Strength);
        col += texture(Texture, pos) * (float(Samples - i) / fSamples) * sampleSize;
    }

    return col *= 2.;

}

void main() {
    fragColor = vec4(radialblur().rgb,1.0);
}
"""

class RadialBlur:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # samples = min(10) max(300) default(124)
            samples = 124
            # strength = min(0.) max(unl) default(0.)
            strength = 0.0
            center = (0.5,0.5) 
        """
        if not tex: return

        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "samples":
                        samples = int(prog.value)
                        self.prog["Samples"] = samples
                if prog.name == "strength":
                        strength = float(prog.value) / 10
                        self.prog["Strength"] = strength
                if prog.name == "center":
                        center = eval(prog.value)
                        self.prog["center"] == center
    
    def render(self,layer_fbo):
          self.tex.use(0)
          layer_fbo.use()
          self.vao.render()

    def add_data(self):
          data = [
                {"key":"samples","value":"124","type":sch.TypVar.TYP_VAR_INT},
                {"key":"strength","value":"0.0","type":sch.TypVar.TYP_VAR_FLOAT},
                {"key":"center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
          ]
          return data
    
    def get_type(self):
          data = [
                {"key":"samples","type":sch.TypVar.TYP_VAR_INT,"min":"10","max":"500"},
                {"key":"strength","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
                {"key":"center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
          ]
          return data
        
        
                              

