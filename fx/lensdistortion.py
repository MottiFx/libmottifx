from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

#define PI 3.141592

uniform vec2 RES;
uniform sampler2D Texture;
uniform float size;
uniform vec2 center;
uniform float zoom;

in vec2 v_uv;
out vec4 fragColor;

vec3 lensdist(vec2 vuv) {
    vec2 p = vuv;
    float prop = RES.x / RES.y;

    // aspect ratio (1:1)
    vec2 p_corr = vec2(p.x,p.y / prop);
    vec2 m_corr = vec2(center.x,center.y / prop);

    vec2 d = p_corr - m_corr; // coordinates
    float r = length(d); // space z effect

    float scale = size / PI;

    float bind;

    float ifscl = step(0.0,scale);
    float bind1 = length(m_corr);
    float bind2 = mix(center.x, center.y / prop, step(1.0,prop));
    bind = mix(bind2,bind1,ifscl);

    vec2 uv;
    uv = p_corr;

    vec2 uvs1 = m_corr + normalize(d) * tan(r * scale) * bind / tan(bind * scale);
    vec2 uvs2 = m_corr + normalize(d) * atan(r * -scale * 10.0) * bind / atan(-scale * bind * 10.0);
    
    uv = mix(uvs2,uvs1,step(0.0,scale));

    uv.y *= prop;
    vec3 col = texture(Texture,uv).xyz;
    return col;
}

vec2 transform(vec2 uv) {
    vec2 pivot = vec2(0.5,0.5);
    uv = (uv - pivot) / zoom + pivot;
    return uv;
}


void main() { 
    vec2 uv = v_uv;
    uv = transform(uv);
    fragColor = vec4(lensdist(uv),1.0);
}

"""

class LensDistortion:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:
            
            center = (0.5,0.5)
            # size = min(unl) max(100+) default(unl)
            size = -1.0
            # zoom = min(0) max(unlimited) default(1.)
            zoom = 1.0
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
                if prog.name == "size":
                    self.prog["size"] = float(prog.value)
                if prog.name == "zoom":
                    self.prog["zoom"] = float(prog.value)
            self.prog["RES"] = self.tex.size
        
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()
    
    def add_data(self):
        data = [
            {"key":"center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key":"zoom","value":"1.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"size","value":"-1.0","type":sch.TypVar.TYP_VAR_MINUS},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"-100.0","max":"100.0"},
            {"key":"zoom","type":sch.TypVar.TYP_VAR_FLOAT,"min":"unl","max":"unl"},
            {"key":"size","type":sch.TypVar.TYP_VAR_MINUS,"min":"unl","max":"unl"},
        ]
        return data

