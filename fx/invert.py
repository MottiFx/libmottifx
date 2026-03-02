from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch


fragment_shader = """
#version 450

uniform sampler2D Texture;
uniform vec3 invert_mask;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec2 uv = v_uv;
    vec4 color = texture(Texture, uv);
    vec3 inverted = mix(color.rgb, vec3(1.0) - color.rgb, invert_mask);
    fragColor = vec4(inverted, color.a);
}
"""


def get_invert_mask(mode):
    mode = mode.lower()
    return {
        "rgb": (1.0, 1.0, 1.0),
        "rg":  (1.0, 1.0, 0.0),
        "rb":  (1.0, 0.0, 1.0),
        "gb":  (0.0, 1.0, 1.0),
        "r":   (1.0, 0.0, 0.0),
        "g":   (0.0, 1.0, 0.0),
        "b":   (0.0, 0.0, 1.0),
        "none":(0.0, 0.0, 0.0),
    }.get(mode, (1.0, 1.0, 1.0))  # default to full invert



class InvertEffect:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Mode:

            "rgb": (1.0, 1.0, 1.0),
            "rg":  (1.0, 1.0, 0.0),
            "rb":  (1.0, 0.0, 1.0),
            "gb":  (0.0, 1.0, 1.0),
            "r":   (1.0, 0.0, 0.0),
            "g":   (0.0, 1.0, 0.0),
            "b":   (0.0, 0.0, 1.0),
            "none":(0.0, 0.0, 0.0),
        """
        if not tex: return
        self.tex = tex
        self.ctx = ctx

        self.prog = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=fragment_shader)
        self.vao = self.ctx.vertex_array(self.prog,vbo,"in_vert","in_tex")

        if progs:
            for prog in progs:
                if prog.name == "invert_mask":
                    self.prog["invert_mask"] = get_invert_mask(prog.value)
    
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"invert_mask","value":"none","type":sch.TypVar.TYP_VAR_OPTION}
        ]

        return data
    
    def get_type(self):
        data = [
            {"key":"invert_mask","type":sch.TypVar.TYP_VAR_OPTION,"min":"unl","max":"unl"}
        ]
        return data
    
    def getlist(self):
        data = ["rgb","rg","rb","gb","r","g","b","none"]
        return data
