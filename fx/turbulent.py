from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

in vec2 v_uv;
out vec4 f_color;

uniform sampler2D Texture;

uniform vec2 center;
uniform vec2 offset;
uniform float scale;
uniform float strength;
uniform int type;
uniform float evolution;
uniform bool keep_edge;
uniform float amount;

// FBM params
uniform int fbm_octaves;
uniform float fbm_frequency;
uniform float fbm_amplitude;
uniform float fbm_amp_mult;
uniform float fbm_seed;

float rand(vec2 p) {
    return fract(sin(dot(p + fbm_seed, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    float a = rand(i);
    float b = rand(i + vec2(1.0, 0.0));
    float c = rand(i + vec2(0.0, 1.0));
    float d = rand(i + vec2(1.0, 1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

float fbm(vec2 p) {
    float total = 0.0;
    float amp = fbm_amplitude;
    vec2 pos = p * fbm_frequency;

    for (int i = 0; i < fbm_octaves; i++) {
        total += noise(pos + evolution) * amp;
        pos *= 2.0;
        amp *= fbm_amp_mult;
    }

    return total;
}

vec4 distort(vec2 uv) {
    vec2 pos = uv - center + offset;
    float freq = 1.0 / max(scale, 0.001);
    float n = fbm(pos * freq);

    vec2 delta = vec2(0.0);

    if (type == 0) {
        delta = vec2(sin(pos.y * 10.0 + n * 6.28), cos(pos.x * 10.0 + n * 6.28));
    } else if (type == 1) {
        float r = length(pos);
        float angle = atan(pos.y, pos.x);
        delta = vec2(sin(angle * 4.0 + n * 6.28), cos(r * 10.0 + n * 6.28));
    } else if (type == 2) {
        float r = length(pos);
        float a = atan(pos.y, pos.x);
        delta = vec2(sin(r * 12.0 + n), cos(a * 8.0 + n));
    } else if (type == 3) {
        delta = vec2(sin(uv.y * 10.0 + n * 6.28), 0.0);
    } else if (type == 4) {
        delta = vec2(0.0, cos(uv.x * 10.0 + n * 6.28));
    } else if (type == 5) {
        float r = length(pos);
        float a = atan(pos.y, pos.x);
        delta = vec2(
            sin(a * 4.0 + n * 6.28) + sin(r * 12.0),
            cos(r * 10.0 + n * 6.28) + cos(a * 8.0)
        );
    }

    vec2 distorted_uv = uv + delta * strength;
    if (keep_edge) {
        distorted_uv = clamp(distorted_uv, 0.0, 1.0);
    }

    vec4 original = texture(Texture, uv);
    vec4 distorted = texture(Texture, distorted_uv);
    return mix(original, distorted, amount);
}

void main() {
    vec2 uv = v_uv;
    f_color = distort(uv);
}


"""

class Turbulent:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None): # NOSONAR
        """
        ### Basics:

            # center = titik effect
            center = (0.5,0.5)
            # offset = default(0.0, 0.0)  offset effect
            offset = (0.0,0.0)
            # scale = min(0) default(1) max(unl)
            scale = 1.
            # strength = free default(0.03)
            strength = 0.03
            # evolution = min(0) max(unl) default(0.2)
            evolution = 0.2
            # keep_edge = with tiles or no default(True)
            keep_edge = True
            # amount = max(1) min(0) default(1.0)
            amount = 1.0

        ### FBM:

            # fbm_octaves = min(0) max(unl) default(6)
            fbm_octaves = 6
            # fbm_frequency = min(0) max(unl) default(2.0)
            fbm_frequency = 2.0
            # fbm_amplitude = min(0) max(unl) default(0.5)
            fbm_amplitude = 0.5
            # fbm_amp_mult = min(0) max(unl) default(0.5)
            fbm_amp_mult = 0.5
            # fbm_seed = min(0) max(unl) default(0.0)
            fbm_seed = 0.0
        """

        if not tex: return

        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
             for prog in progs:
                 if prog.name == "center":
                     self.prog["center"] = eval(prog.value)
                 if prog.name == "offset":
                     self.prog["offset"] = eval(prog.value)
                 if prog.name == "scale":
                     self.prog["scale"] = float(prog.value)
                 if prog.name == "strength":
                     self.prog["strength"] = float(prog.value)
                 if prog.name == "evolution":
                     self.prog["evolution"] = float(prog.value)
                 if prog.name == "keep_edge":
                     self.prog["keep_edge"] = eval(prog.value)
                 if prog.name == "amount":
                     self.prog["amount"] = float(prog.value)
                 # fbm
                 if prog.name == "fbm_octaves":
                     self.prog["fbm_octaves"] = int(prog.value)
                 if prog.name == "fbm_frequency":
                     self.prog["fbm_frequency"] = float(prog.value)
                 if prog.name == "fbm_amplitude":
                     self.prog["fbm_amplitude"] = float(prog.value)
                 if prog.name == "fbm_amp_mult":
                     self.prog["fbm_amp_mult"] = float(prog.value)
                 if prog.name == "fbm_seed":
                     self.prog["fbm_seed"] = float(prog.value)

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key":"offset","value":"(0.0,0.0)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key":"scale","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"strength","value":"0.03","type":sch.TypVar.TYP_VAR_MINUS},
            {"key":"evolution","value":".2","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"keep_edge","value":"True","type":sch.TypVar.TYP_VAR_BOOL},
            {"key":"amount","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"fbm_octaves","value":"6","type":sch.TypVar.TYP_VAR_INT},
            {"key":"fbm_frequency","value":"2.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"fbm_amplitude","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"fbm_amp_mult","value":"0.5","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"fbm_seed","value":"0.0","type":sch.TypVar.TYP_VAR_FLOAT},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key":"offset","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key":"scale","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
            {"key":"strength","type":sch.TypVar.TYP_VAR_MINUS,"min":"unl","max":"unl"},
            {"key":"evolution","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"keep_edge","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
            {"key":"amount","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key":"fbm_octaves","type":sch.TypVar.TYP_VAR_INT,"min":"0","max":"unl"},
            {"key":"fbm_frequency","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"fbm_amplitude","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"fbm_amp_mult","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
            {"key":"fbm_seed","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.","max":"unl"},
        ]
        return data
