from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float steps;
uniform bool VRGB;
uniform float hue;
uniform float saturate;
uniform float amount;

in vec2 v_uv;
out vec4 fragColor;


vec3 rgb2hsv(vec3 c)
{
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

void main() {
    vec2 uv = v_uv;
    vec4 texCol = texture(Texture,uv);
    vec3 hsv = rgb2hsv(texCol.rgb);


    float posterizeAmount = amount;
    float posterizeSteps = steps;

    float posterizeStepsHue = hue;
    float posterizeStepsSaturation = saturate;

    if (VRGB) {
        vec3 posterizeSteps = vec3(posterizeStepsHue, posterizeStepsSaturation, posterizeSteps);
        vec3 posterizedHsv = round(hsv * posterizeSteps) / posterizeSteps;

        vec3 posterizedRgb = hsv2rgb(posterizedHsv);
        vec3 blended = mix(texCol.rgb, posterizedRgb, posterizeAmount);

        fragColor = vec4(blended, texCol.a);
    }
    else {
        vec3 posterizeSteps = vec3(posterizeSteps,posterizeSteps,posterizeSteps);
        vec3 posterized = round(texCol.rgb * posterizeSteps) / posterizeSteps;

        vec3 blended = mix(texCol.rgb, posterized, posterizeAmount);

        fragColor = vec4(blended, texCol.a);
    
    }

}
"""


class Posterize:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None): # NOSONAR
        """
        ### Basics:

            # hue = min(1) max(unlimited) default(8192.0)
            hue = 8192.0
            # saturate = min(1) max(unlimited) default(8192.0)
            saturate = 8192.0
            # steps = min(1) max(50) default(5.0)
            steps = 5.0
            # amount = min(0) max(1) default(0.7)
            amount = 0.7
            # vrgb = True Or False default(False)
            vrgb = False
        """

        if not tex: return

        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "hue":
                    self.prog["hue"] = float(prog.value)
                if prog.name == "saturate":
                    self.prog["saturate"] = float(prog.value)
                if prog.name == "steps":
                    self.prog["steps"] = float(prog.value)
                if prog.name == "amount":
                    self.prog["amount"] = float(prog.value)
                if prog.name == "vrgb":
                    self.prog["VRGB"] = eval(prog.value)
    
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"hue","value":"99.99","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"saturate","value":"99.99","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"steps","value":"5.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"amount","value":"0.7","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"vrgb","value":"False","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data

    def get_type(self):
        data = [
            {"key":"hue","type":sch.TypVar.TYP_VAR_FLOAT,"min":"1.0","max":"unl"},
            {"key":"saturate","type":sch.TypVar.TYP_VAR_FLOAT,"min":"1.0","max":"unl"},
            {"key":"steps","type":sch.TypVar.TYP_VAR_FLOAT,"min":"1.0","max":"50.0"},
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key":"vrgb","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
