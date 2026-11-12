from ocrlib.registry import Registry

WRITERS = Registry("writer")

from ocrlib.writers.json import JsonWriter

WRITERS.register(JsonWriter())
