from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def test_resized_palette_gif_keeps_transparent_pixels():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.STORAGE = "thumbor.storages.no_storage"
    context = Context(config=cfg)

    # Palette entry 0 is fully transparent, entry 1 is opaque blue.
    source = Image.new("P", (40, 40), 1)
    for x in range(20):
        for y in range(40):
            source.putpixel((x, y), 0)
    palette = [0, 0, 0, 0, 0, 255] + [0] * (256 * 3 - 6)
    source.putpalette(palette)

    buffer = BytesIO()
    source.save(buffer, "PNG", transparency=0)

    engine = Engine(context)
    engine.load(buffer.getvalue(), ".png")
    assert engine.original_mode == "P"
    engine.resize(20, 20)

    out = Image.open(BytesIO(engine.read(".gif")))
    assert "transparency" in out.info

    alpha = out.convert("RGBA").split()[3]
    transparent_pixels = sum(1 for value in alpha.getdata() if value == 0)
    assert transparent_pixels > 0
