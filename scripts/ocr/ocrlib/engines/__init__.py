from ocrlib.registry import Registry

ENGINES = Registry("engine")

from ocrlib.engines.hunyuanocr import HunyuanOcrEngine

ENGINES.register(HunyuanOcrEngine)
