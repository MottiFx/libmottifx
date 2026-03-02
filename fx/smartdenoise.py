from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader ="""   
#version 450

#define DISTRIBUTION_BIAS 0.6 // between 0. and 1.
#define PIXEL_MULTIPLIER  1.5 // between 1. and 3. (keep low)
#define INVERSE_HUE_TOLERANCE 20.0 // (2. - 30.)

#define GOLDEN_ANGLE 2.3999632 //3PI-sqrt(5)PI

#define pow(a,b) pow(max(a,0.),b) // Ib @Zerofile shadertoy

uniform float samples;
uniform vec2 resolution;
uniform sampler2D Texture;

in vec2 v_uv;
out vec4 fragColor;

mat2 sample2D = mat2(cos(GOLDEN_ANGLE),sin(GOLDEN_ANGLE),-sin(GOLDEN_ANGLE),cos(GOLDEN_ANGLE));

vec3 birdDenoise() {
    vec3 denoisedColor = vec3(0.);
    vec2 uv = v_uv;
    
    const float sampleRadius =  sqrt(samples);
    const float sampleTrueRadius  = 0.5 / (sampleRadius*sampleRadius);
    vec2 samplePixel = vec2(1.0/resolution.x,1.0/resolution.y);
    vec3 sampleCenter = texture(Texture,uv).rgb;
    vec3 sampleCenterNorm = normalize(sampleCenter);
    float sampleCenterSat = length(sampleCenter);

    float influenceSum = 0.0;
    float brightnessSum = 0.0;

    vec2 pixelRotated = vec2(0.,1.);

    for(float x = 0.0; x <= samples; x++){
    
        pixelRotated *= sample2D;

        vec2 pixelOffset = PIXEL_MULTIPLIER*pixelRotated*sqrt(x)*0.5;
        float pixelInfluence = 1.0-sampleTrueRadius*pow(dot(pixelOffset,pixelOffset),DISTRIBUTION_BIAS);
        pixelOffset *= samplePixel;

        vec3 thisDenoisedColor = texture(Texture,uv+pixelOffset).rgb;
        pixelInfluence *= pixelInfluence*pixelInfluence;
        
        pixelInfluence *= pow(0.5+0.5*dot(sampleCenterNorm,normalize(thisDenoisedColor)),INVERSE_HUE_TOLERANCE)*pow(1.0-abs(length(thisDenoisedColor)-length(sampleCenterSat)),8.);

        influenceSum += pixelInfluence;
        denoisedColor += thisDenoisedColor*pixelInfluence;
    }

    return denoisedColor/influenceSum;
}


void main() {
    fragColor = vec4(birdDenoise().rgb,1.0);
}


"""

class SmartDenoise:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # samples = min(1) max(100) default(10.)
            samples = 10.0
        """

        if not tex: return

        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "samples":
                    samples = float(prog.value)
                    self.prog["samples"] = samples
            self.prog["resolution"] = tex.size

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"samples","value":"10.0","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"samples","type":sch.TypVar.TYP_VAR_FLOAT,"min":"1.0","max":"100.0"}
        ]
        return data
