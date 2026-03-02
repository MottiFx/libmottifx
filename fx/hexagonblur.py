
from procmottifx.systems.protos import schema_pb2 as sch


frg_common = """
#version 450

uniform float highlight;
uniform sampler2D Texture;
uniform float sizeS;
uniform vec2 RES;

float u_Angle = 0.0;

in vec2 v_uv;
out vec4 fragColor;

float customStep(float edge0, float edge1, float value) {
    return clamp((value - edge0) / (edge1 - edge0), 0.0, 1.0);
}

float getScale(float p) {
    return customStep(1.0, 0.0, p);
}

vec4 gaussianBlur(sampler2D i_InputTex, vec2 i_Uv, vec2 i_Dir, float i_Strength)
{
    float half_gaussian_weight[9];
    half_gaussian_weight[0]= 0.20;//0.137401;
    half_gaussian_weight[1]= 0.19;//0.125794;
    half_gaussian_weight[2]= 0.17;//0.106483;
    half_gaussian_weight[3]= 0.15;//0.080657;
    half_gaussian_weight[4]= 0.13;//0.054670;
    half_gaussian_weight[5]= 0.11;//0.033159;
    half_gaussian_weight[6]= 0.08;//0.017997;
    half_gaussian_weight[7]= 0.05;//0.008741;
    half_gaussian_weight[8]= 0.02;//0.003799;
    vec4 sum            = vec4(0.0);
    vec4 result         = vec4(0.0);
    vec2 unit_uv        = i_Dir * i_Strength;
    vec4 curColor       = texture(i_InputTex, i_Uv);
    vec4 centerPixel    = curColor*half_gaussian_weight[0];
    float sum_weight    = half_gaussian_weight[0];
    for(int i=1;i<=8;i++)
    {
        vec2 curRightCoordinate = i_Uv+float(i)*unit_uv;
        vec2 curLeftCoordinate  = i_Uv+float(-i)*unit_uv;
        vec4 rightColor = texture(i_InputTex, curRightCoordinate);
        vec4 leftColor = texture(i_InputTex, curLeftCoordinate);
        sum+=rightColor*half_gaussian_weight[i];
        sum+=leftColor*half_gaussian_weight[i];
        sum_weight+=half_gaussian_weight[i]*2.0;
    }
    result = (sum+centerPixel)/sum_weight; 
    return result;
}

vec4 dirBlur(sampler2D inputTexture, vec2 uv, vec2 dir, float p)
{
    float weight = 1.0;
    float u_Size = 0.41;
    float u_Bright = 4.8;
    
    float u_SizeScale = getScale(p);
    vec4 resColor = texture(inputTexture, uv);
    float sumWeight = 1.0;
    vec4 maxColor = resColor;
    for (int i = 1; i <= 16; ++i)
    {
        vec2 tmpUV = uv + dir * float(i) * u_Size * u_SizeScale;
        vec4 a = texture(inputTexture, tmpUV);
        tmpUV = uv - dir * float(i) * u_Size * u_SizeScale;
        vec4 b = texture(inputTexture, tmpUV);
        resColor += a + b;
        vec4 c = max(a, b);
        maxColor = max(c, maxColor);
        sumWeight += 2.0;
    }
    
    resColor /= sumWeight;
    vec4 color = mix(resColor, maxColor, clamp(resColor * u_Bright, 0.0, 1.0));
    resColor.rgb = color.rgb;
    return resColor;
}

"""

frg_A = frg_common + "\n" + """

void main() {
    vec2 uv = v_uv;
    float theta = radians(u_Angle);
    float u_SizeScale = getScale(sizeS);

    vec2 rect = vec2(min(720.0, 720.0 * RES.x / RES.y), min(720.0, 720.0 * RES.y / RES.x));
    vec2 dir = vec2(cos(theta), sin(theta)) / rect.xy;

    vec4 color = gaussianBlur(Texture, uv, dir, highlight * u_SizeScale);
    fragColor = color;
    
}

"""

frg_B = frg_common + "\n" + """

void main() {
    u_Angle = 90.0;
    vec2 uv = v_uv;
    float theta = radians(u_Angle);
    float u_SizeScale = getScale(sizeS);

    vec2 rect = vec2(min(720.0, 720.0 * RES.x / RES.y), min(720.0, 720.0 * RES.y / RES.x));
    vec2 dir = vec2(cos(theta), sin(theta)) / rect.xy;

    vec4 color = gaussianBlur(Texture, uv, dir, highlight * u_SizeScale);
    fragColor = color;
    
}

"""

frg_C = frg_common + "\n" + """

void main() {
    u_Angle = 60.0;
    vec2 uv = v_uv;
    float theta = radians(u_Angle);
    vec2 rect = vec2(min(720.0, 720.0 * RES.x / RES.y), min(720.0, 720.0 * RES.y / RES.x));
    vec2 dir = vec2(cos(theta), sin(theta)) / rect;
    vec4 color = dirBlur(Texture, uv, dir, sizeS);
    fragColor = color;
}

"""

frg_D = frg_common + "\n" + """

void main() {
    u_Angle = -60.0;
    vec2 uv = v_uv;
    float theta = radians(u_Angle);
    vec2 rect = vec2(min(720.0, 720.0 * RES.x / RES.y), min(720.0, 720.0 * RES.y / RES.x));
    vec2 dir = vec2(cos(theta), sin(theta)) / rect;
    vec4 color = dirBlur(Texture, uv, dir, sizeS);
    fragColor = color;
}

"""

frg_Img = frg_common + "\n" + """

void main() {
    float PI = 3.1415926;
    u_Angle = 0.0;
    vec2 uv = v_uv;
    float theta = u_Angle * PI / 180.0;
    vec2 rect = vec2(min(720.0, 720.0 * RES.x / RES.y), min(720.0, 720.0 * RES.y / RES.x));
    vec2 dir = vec2(cos(theta), sin(theta)) / rect;
    vec4 color = dirBlur(Texture, uv, dir, sizeS);
    fragColor = color;
}

"""

class HexagonBlur:
    def __init__(
            self,
            tex=None,
            ctx=None,
            vertex_shader=None,
            vbo=None,
            out_size=None,
            progs=None,
            itime=None
            ):
        """
        ### Basics:

            # sizes = min(0.0) max(1.0) default(0.2)
            sizes = 0.2
            # highlight = min(0.0) max(unl) default(0.32)
            highlight = 0.32
        """

        if not tex: return
        w,h = tex.size

        self.tex = tex
        self.ctx = ctx

        self.prog_a = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=frg_A)
        self.prog_b = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=frg_B)
        self.prog_c = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=frg_C)
        self.prog_d = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=frg_D)
        self.prog_img = self.ctx.program(vertex_shader=vertex_shader,fragment_shader=frg_Img)        
        
        if progs:
            for prog in progs:
                for progn in [self.prog_a, self.prog_b]:
                    if prog.name == "higlight":
                        progn["highlight"] = float(prog.value)
                    if prog.name == "sizeS":
                        progn["sizeS"] = float(prog.value)
                    progn["RES"] = (w, h)

                for progn in [self.prog_c, self.prog_d, self.prog_img]:
                    if prog.name == "sizeS":
                        progn["sizeS"] = float(prog.value)
                    progn["RES"] = (w, h)

        self.tex_a = ctx.texture((w,h),4)
        self.fbo_a = ctx.framebuffer(color_attachments=[self.tex_a])

        self.tex_b = ctx.texture((w,h),4)
        self.fbo_b = ctx.framebuffer(color_attachments=[self.tex_b])

        self.tex_c = ctx.texture((w,h),4)
        self.fbo_c = ctx.framebuffer(color_attachments=[self.tex_c])

        self.tex_d = ctx.texture((w,h),4)
        self.fbo_d = ctx.framebuffer(color_attachments=[self.tex_d])

        # VAO untuk masing-masing shader
        self.vao_a = self.ctx.vertex_array(self.prog_a,vbo, "in_vert", "in_tex")
        self.vao_b = self.ctx.vertex_array(self.prog_b,vbo, "in_vert", "in_tex")
        self.vao_c = self.ctx.vertex_array(self.prog_c,vbo, "in_vert", "in_tex")
        self.vao_d = self.ctx.vertex_array(self.prog_d,vbo, "in_vert", "in_tex")
        self.vao_img = self.ctx.vertex_array(self.prog_img,vbo, "in_vert", "in_tex")


    def render(self,layer_fbo):
        self.fbo_a.use()
        self.tex.use(0)
        self.vao_a.render()

        self.fbo_b.use()
        self.tex_a.use(0)
        self.vao_b.render()

        self.fbo_c.use()
        self.tex_b.use(0)
        self.vao_c.render()

        self.fbo_d.use()
        self.tex_c.use(0)
        self.vao_d.render()

        self.tex_d.use(0)
        layer_fbo.use()
        self.vao_img.render()
    
    def add_data(self):
        data = [
            {"key":"sizeS","value":"0.2","type":sch.TypVar.TYP_VAR_FLOAT},
            {"key":"higlight","value":"0.32","type":sch.TypVar.TYP_VAR_FLOAT}
        ]
        return data

    def get_type(self):
        data = [
            {"key": "sizeS","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"1.0"},
            {"key": "higlight","type":sch.TypVar.TYP_VAR_FLOAT,"min":"0.0","max":"unl"},
        ]
        return data
