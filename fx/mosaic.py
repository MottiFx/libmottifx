from typing import Tuple
from procmottifx.systems.protos import schema_pb2 as sch

fragment_shader = """
#version 450

uniform float size;
uniform sampler2D Texture;
uniform vec2 resolution;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec2 uv = v_uv;
    uv.x = ceil(uv.x * resolution.x / size) * size / resolution.x;
    uv.y = ceil(uv.y * resolution.y / size) * size / resolution.y;

    fragColor = texture(Texture,uv);
}
"""

class Mosaic:
    def __init__(self,tex=None,ctx=None,vertex_shader=None,vbo=None,out_size: Tuple[int,int]=None,progs = None,itime=None):
        """
        ### Basics:

            # size = min(1) max(100)
            size = 10.0
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
            self.prog["resolution"] = out_size

    
    def render(self,layer_fbo):
        self.tex.use(0)
        layer_fbo.use()
        self.vao.render()

    def add_data(self):
        data = [
            {"key":"size","value":"10.0","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data
    
    def get_type(self):
        data = [
            {"key":"size","type":sch.TypVar.TYP_VAR_FLOAT,"min":"1.0","max":"100.0"}
        ]
        return data
