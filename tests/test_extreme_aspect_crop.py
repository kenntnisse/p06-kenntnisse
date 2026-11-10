from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine
from thumbor.transformer import Transformer


def test_extreme_aspect_ratio_returns_visible_picture():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
    )
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.STORAGE = "thumbor.storages.no_storage"
    context = Context(config=cfg)

    # 16x16 source with colored vertical bars, fully opaque.
    source = Image.new("RGBA", (16, 16))
    for x in range(16):
        for y in range(16):
            source.putpixel((x, y), (x * 16, 255 - x * 16, 128, 255))
    buffer = BytesIO()
    source.save(buffer, "PNG")

    engine = Engine(context)
    engine.load(buffer.getvalue(), ".png")

    context.request = SimpleNamespace(
        engine=engine,
        width=800,
        height=20,
        fit_in=False,
        stretch=False,
        full=False,
        adaptive=False,
        focal_points=[],
        should_crop=False,
        crop=None,
        halign="center",
        valign="middle",
        debug=False,
        horizontal_flip=False,
        vertical_flip=False,
    )

    transformer = Transformer(context)
    transformer.img_operation_worker()

    assert engine.size == (800, 20)

    alpha = engine.image.convert("RGBA").split()[3]
    assert alpha.getextrema()[1] > 0
