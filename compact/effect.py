from libmottifx.fx.bokeh import Bokeh
from libmottifx.fx.findedge import FindEdge
from libmottifx.fx.flip import Flip
from libmottifx.fx.glow import Glow
from libmottifx.fx.grain import Grain
from libmottifx.fx.mosaic import Mosaic
from libmottifx.fx.audsfx import AudioSfx
from libmottifx.fx.basics.transform import TransformObj
from libmottifx.fx.chromatic import Chromatic
from libmottifx.fx.hexagonblur import HexagonBlur
from libmottifx.fx.invert import InvertEffect
from libmottifx.fx.lensdistortion import LensDistortion
from libmottifx.fx.lumafade import LumaFade
from libmottifx.fx.posterize import Posterize
from libmottifx.fx.radialblur import RadialBlur
from libmottifx.fx.rainy import Rainy
from libmottifx.fx.sharpen import Sharpen
from libmottifx.fx.smartdenoise import SmartDenoise
from libmottifx.fx.starglow import StarGlow
from libmottifx.fx.swirl import Swirl
from libmottifx.fx.turbulent import Turbulent
from libmottifx.fx.usharpmask import UsharpMask
from libmottifx.fx.vignette import Vignette
from procmottifx.systems.protos import schema_pb2 as sch


LISTEFFECT = [
    {"typfx":sch.TypFx.TYP_FX_TRANSFORM_2D,"func":TransformObj,"name":"Transform","basic": True},
    {"typfx":sch.TypFx.TYP_FX_CHROMATIC,"func":Chromatic,"name":"Chromatic","basic": False},
    {"typfx":sch.TypFx.TYP_FX_HEXAGON_BLUR,"func":HexagonBlur,"name":"HexagonBlur","basic": False},
    {"typfx":sch.TypFx.TYP_FX_INVERT,"func":InvertEffect,"name":"Invert","basic": False},
    {"typfx":sch.TypFx.TYP_FX_LUMAFADE,"func":LumaFade,"name":"LumaFade","basic": False},
    {"typfx":sch.TypFx.TYP_FX_SHARPEN,"func":Sharpen,"name":"Sharpen","basic": False},
    {"typfx":sch.TypFx.TYP_FX_RADIALBLUR,"func":RadialBlur,"name":"RadialBlur","basic": False},
    {"typfx":sch.TypFx.TYP_FX_SWIRL,"func":Swirl,"name":"Swirl","basic": False},
    {"typfx":sch.TypFx.TYP_FX_SMART_DENOISE,"func":SmartDenoise,"name":"SmartDenoise","basic": False},
    {"typfx":sch.TypFx.TYP_FX_STARGLOW,"func":StarGlow,"name":"StarGlow","basic": False},
    {"typfx":sch.TypFx.TYP_FX_MOSAIC,"func":Mosaic,"name":"Mosaic","basic": False},
    {"typfx":sch.TypFx.TYP_FX_LENS_DIST,"func":LensDistortion,"name":"LensDistortion","basic": False},
    {"typfx":sch.TypFx.TYP_FX_GRAIN,"func":Grain,"name":"Grain","basic": False},
    {"typfx":sch.TypFx.TYP_FX_BOKEH,"func":Bokeh,"name":"Bokeh","basic": False},
    {"typfx":sch.TypFx.TYP_FX_EDGE,"func":FindEdge,"name":"FindEdge","basic": False},
    {"typfx":sch.TypFx.TYP_FX_GLOW,"func":Glow,"name":"Glow","basic": False},
    {"typfx":sch.TypFx.TYP_FX_RAINY,"func":Rainy,"name":"Rainy","basic": False},
    {"typfx":sch.TypFx.TYP_FX_POSTERIZE,"func":Posterize,"name":"Posterize","basic": False},
    {"typfx":sch.TypFx.TYP_FX_UNSHARPMASK,"func":UsharpMask,"name":"UsharpMask","basic": False},
    {"typfx":sch.TypFx.TYP_FX_TURBULENT,"func":Turbulent,"name":"Turbulent","basic": False},
    {"typfx":sch.TypFx.TYP_FX_VIGNETTE,"func":Vignette,"name":"Vignette","basic": False},
    {"typfx":sch.TypFx.TYP_FX_FLIP,"func":Flip,"name":"Flip","basic": False},
]   

LISTAUDFX = [
    {"typfx":sch.TypFx.TYP_FX_BASICAUDIO,"func":AudioSfx,"name":"Audio","basic": True}
]