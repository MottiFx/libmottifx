from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch
from guimottifx.utils.configediting import ConfigTimeLine


fragment_shader = """
#version 450

#define PI 6.28318530718
#define S(a, b, t) smoothstep(a, b, t)
uniform sampler2D Texture;
uniform vec2 RES;

// Size Rainy
uniform float size;
uniform float iTime;

// Blur Set
uniform float quality;
uniform float direction;
uniform float sizeBlur;

in vec2 v_uv;
out vec4 fragColor;

vec3 N13(float p){
    vec3 p3 = fract(vec3(p) * vec3(.1031,.11369,.13787));
    p3 += dot(p3, p3.yzx + 19.19);
    return fract(vec3((p3.x + p3.y)*p3.z, (p3.x+p3.z)*p3.y, (p3.y+p3.z)*p3.x));
}

vec4 N14(float t) {
	return fract(sin(t*vec4(123., 1024., 1456., 264.))*vec4(6547., 345., 8799., 1564.));
}

float N(float t) {
    return fract(sin(t*12345.564)*7658.76);
}

float Saw(float b, float t) {
	return S(0., b, t)*S(1., b, t);
}

vec2 Drops(vec2 uv, float t) {
    
    vec2 UV = uv;
    
    // DEFINE GRID
    uv.y += t*0.8;
    vec2 a = vec2(6., 1.);
    vec2 grid = a*2.;
    vec2 id = floor(uv*grid);
    
    // RANDOM SHIFT Y
    float colShift = N(id.x); 
    uv.y += colShift;
    
    // DEFINE SPACES
    id = floor(uv*grid);
    vec3 n = N13(id.x*35.2+id.y*2376.1);
    vec2 st = fract(uv*grid)-vec2(.5, 0);
    
    // POSITION DROPS
    //clamp(2*x,0,2)+clamp(1-x*.5, -1.5, .5)+1.5-2
    float x = n.x-.5;
    
    float y = UV.y*20.;
    
    float distort = sin(y+sin(y));
    x += distort*(.5-abs(x))*(n.z-.5);
    x *= .7;
    float ti = fract(t+n.z);
    y = (Saw(.85, ti)-.5)*.9+.5;
    vec2 p = vec2(x, y);
    
    // DROPS
    float d = length((st-p)*a.yx);
    
    float dSize = size; 
    
    float Drop = S(dSize, .0, d);
    
    
    float r = sqrt(S(1., y, st.y));
    float cd = abs(st.x-x);
    
    // TRAILS
    float trail = S((dSize*.5+.03)*r, (dSize*.5-.05)*r, cd);
    float trailFront = S(-.02, .02, st.y-y);
    trail *= trailFront;
    
    
    // DROPLETS
    y = UV.y;
    y += N(id.x);
    float trail2 = S(dSize*r, .0, cd);
    float droplets = max(0., (sin(y*(1.-y)*120.)-st.y))*trail2*trailFront*n.z;
    y = fract(y*10.)+(st.y-.5);
    float dd = length(st-vec2(x, y));
    droplets = S(dSize*N(id.x), 0., dd);
    float m = Drop+droplets*r*trailFront;
    return vec2(m, trail);
}


float StaticDrops(vec2 uv, float t) {
	uv *= 30.;
    
    vec2 id = floor(uv);
    uv = fract(uv)-.5;
    vec3 n = N13(id.x*107.45+id.y*3543.654);
    vec2 p = (n.xy-.5)*0.5;
    float d = length(uv-p);
    
    float fade = Saw(.025, fract(t+n.z));
    float c = S(size, 0., d)*fract(n.z*10.)*fade;

    return c;
}

vec2 Rain(vec2 uv, float t) {
    float s = StaticDrops(uv, t); 
    vec2 r1 = Drops(uv, t);
    vec2 r2 = Drops(uv*1.8, t);
    float c = s+r1.x+r2.x;
    c = S(.3, 1., c);
    return vec2(c, max(r1.y, r2.y));
}

void main() {
    vec2 uv = v_uv;
    float T = iTime;

    float t = T*.2;

    uv = (uv-.5) * (.9) + .5;
    vec2 c = Rain(uv,t);

    vec2 e = vec2(.001,0.);
    float cx = Rain(uv+e,t).x;
    float cy = Rain(uv+e.yx,t).x;
    vec2 n = vec2(cx-c.x,cy-c.x);

    vec2 Radius = sizeBlur/RES.xy;
    vec3 col = texture(Texture,uv).rgb;

    for(float d =0.0; d<float(PI);d+=float(PI)/direction) {
        for(float i = 1.0/quality; i<=1.0; i+=1.0/quality) {
            vec3 tex = texture(Texture, uv+n+vec2(cos(d),sin(d))*Radius*i).rgb;

            col += tex;
        }
    
    }

    col /= quality * direction - 0.0;

    vec3 tex = texture(Texture,uv+n).rgb;
    c.y = clamp(c.y,0.0,1.);

    col -= c.y;
    col += c.y*(tex+.6);

    fragColor = vec4(col,1.);
}
"""

class Rainy:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None): # NOSONAR
        """
        ### Rainy:

            # size = min(0) max(1) default(.2)
            size = 0.2

        ### Blur:

            # sizeblur = min(0) max(100) default(32.0)
            sizeblur = 32.0
            # direction = min(16) max(unlimited) default(32)
            direction = 32.0
            # quality = min(4) max(unlimited) default(8) 
            quality = 8.0
        """


        if not tex: return

        self.ctx = ctx
        self.tex = tex

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "size":
                    self.prog["size"] = float(prog.value)
                if prog.name == "sizeblur":
                    self.prog["sizeBlur"] = float(prog.value)
                if prog.name == "direction":
                    self.prog["direction"] = float(prog.value)
                if prog.name == "quality":
                    self.prog["quality"] = float(prog.value)
            self.prog["iTime"] = itime
            self.prog["RES"] = self.tex.size

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"size","value":"0.2","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"sizeblur","value":"32.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"direction","value":"32.0","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"quality","value":"8.0","type":sch.TypVar.TYP_VAR_FLOAT},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"size","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key":"sizeblur","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"100.0"},
            {"key":"direction","type":sch.TypVar.TYP_VAR_FLOAT,"min":"16.0","max":"unl"},
            {"key":"quality","type":sch.TypVar.TYP_VAR_FLOAT,"min":"4.0","max":"unl"},
        ]
        return data
