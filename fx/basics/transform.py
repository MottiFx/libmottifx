
import math
from typing import Tuple

from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform float angle;
uniform vec2 scale;
uniform vec2 translate;
uniform vec2 RES;
uniform vec2 center;
uniform float opacity;
#define PI 3.1415926535
uniform bool mirror_edge;
uniform bool mirror_tile;

in vec2 v_uv;
out vec4 fragColor;


vec2 tile_coords(vec2 uv,int mirror_layer) {
    uv *= mirror_layer;

    vec2 tile = floor(uv);
    vec2 local_uv = fract(uv);

    if (mirror_layer % 2 != 0) {

        if (int(tile.x) % 2 == 0) {
            if (mirror_edge) {
                local_uv.x = 1.0 - local_uv.x;
            }
            else {
                local_uv.x = 1.0 + local_uv.x;
            }
        }

        if (int(tile.y) % 2 == 0) {
            if (mirror_edge) {
                local_uv.y = 1.0 - local_uv.y;
            }
            else {
                local_uv.y = 1.0 + local_uv.y;
            }
        }
    
    }

    if (mirror_layer % 2 == 0) {

        if (int(tile.x) % 2 == 1) {
            if (mirror_edge) {
                local_uv.x = 1.0 - local_uv.x;
            }
            else {
                local_uv.x = 1.0 + local_uv.x;
            }
        }

        if (int(tile.y) % 2 == 1) {
            if (mirror_edge) {
                local_uv.y = 1.0 - local_uv.y;
            }
            else {
                local_uv.y = 1.0 + local_uv.y;
            }
        }
    
    }

    return local_uv;
}

vec2 transform(vec2 uv,vec2 newscale) {
    vec2 pivot = center;
    uv -= pivot;

    // fix aspect ratio
    uv.x *= RES.x / RES.y;

    // scale and rotation
    float cosine = cos(angle);
    float sine = sin(angle);

    mat2 ScaleAndRotation = mat2(
        cosine / newscale.x, -sine  / newscale.x,
        sine   / newscale.y, cosine / newscale.y
    );

    uv *= ScaleAndRotation;

    // translate
    uv += translate;

    // normal coord
    uv.x /= (RES.x / RES.y); // fix aspect ration again
    uv += pivot;

    return uv;
}

void main() {
    vec2 uv = v_uv;
    vec2 newscale = scale;

    const int layer = 5;
    const int tiles = layer * 2 + 1;
    int mirror_layer = tiles;
    

    if (mirror_tile) {
        newscale *= mirror_layer;
    }

    uv = transform(uv,newscale);

    if (mirror_tile){
        uv = tile_coords(uv,mirror_layer);
    }
    vec4 texColor = texture(Texture,uv);

    // remove tile
    if (!mirror_tile && (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0))
        fragColor = vec4(0.0);
    else
        fragColor = vec4(texColor.rgb,texColor.a * opacity);
}
"""

class TransformObj:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # scale = min(unl) max(unl)
            scale = (1.0,1.0)
            # translate = min(unl) max(unl)
            translate = (0.0,0.0)
            # center = min(unl) max(unl)
            center = (0.5,0.5)
            # angle = min(unl) max(unl)
            angle = 0.
            # opacity = min(0.) max(1.0)
            opacity = 1.
            # mirror_tile = min(unl) max(unl)
            mirror_tile = False
            # mirror_edge = min(unl) max(unl)
            mirror_edge = False
        """
        if not tex: return
        w,h = tex.size
        out_w,out_h = out_size

        self.tex = tex
        self.ctx = ctx
        
        self.prog = ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = ctx.vertex_array(self.prog,vbo,"in_vert", "in_tex")

        aspect_ratio = out_w / out_h
        layer_ratio = w / h

        if layer_ratio > aspect_ratio:
            fit_w = out_w
            fit_h = int(fit_w / layer_ratio)
        else:
            fit_h = out_h
            fit_w = layer_ratio * fit_h

        scale_x = fit_w / out_w
        scale_y = fit_h / out_h

        prog = {prog.name: prog.value for prog in progs}
        if "scale" in prog:
            scale = eval(prog["scale"])
            self.prog["scale"] = (scale[0]*scale_x,scale[1]*scale_y)
        if "translate" in prog:
            translate = eval(prog["translate"])
            self.prog["translate"] = translate
        if "center" in prog:
            center = eval(prog["center"])
            self.prog["center"] = center
        if "angle" in prog:
            angle = float(prog["angle"])
            self.prog["angle"] = math.radians(angle)
        if "opacity" in prog:
            opacity = float(prog["opacity"])
            self.prog["opacity"] = opacity
        if "mirror_tile" in prog:
            self.prog["mirror_tile"] = eval(prog["mirror_tile"])
        if "mirror_edge" in prog:
            self.prog["mirror_edge"] = eval(prog["mirror_edge"])
        self.prog["RES"] = (out_w,out_h)

        # self.fbo = ctx.framebuffer(color_attachments=[ctx.texture((out_w,out_h), 4)],)
    

    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key": "scale","value":"(1.,1.)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key": "translate","value":"(0.,0.)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key": "center","value":"(0.5,0.5)","type":sch.TypVar.TYP_VAR_TUPLE},
            {"key": "angle","value":"0.","type":sch.TypVar.TYP_VAR_MINUS},
            {"key": "opacity","value":"1.","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key": "mirror_tile","value":"False","type":sch.TypVar.TYP_VAR_BOOL},
            {"key": "mirror_edge","value":"False","type":sch.TypVar.TYP_VAR_BOOL},
        ]
        return data
    
    def get_type(self):
        data = [
            {"key": "scale","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key": "translate","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key": "center","type":sch.TypVar.TYP_VAR_TUPLE,"min":"unl","max":"unl"},
            {"key": "angle","type":sch.TypVar.TYP_VAR_MINUS,"min":"unl","max":"unl"},
            {"key": "opacity","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key": "mirror_tile","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
            {"key": "mirror_edge","type":sch.TypVar.TYP_VAR_BOOL,"min":"unl","max":"unl"},
        ]
        return data
