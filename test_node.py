from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from nodes import _draw_bubble, _panel_boxes


def main():
    width, height = 1344, 1856
    page = Image.new("RGB", (width, height), "#f4f2ed")
    draw = ImageDraw.Draw(page)
    margin, gutter = 45, 24
    panel_w = (width - margin * 2 - gutter) // 2
    panel_h = (height - margin * 2 - gutter) // 2
    colors = ["#d7e7ef", "#e9ddd0", "#dce8d4", "#ead7df"]
    boxes = [
        (margin, margin, margin + panel_w, margin + panel_h),
        (margin + panel_w + gutter, margin, width - margin, margin + panel_h),
        (margin, margin + panel_h + gutter, margin + panel_w, height - margin),
        (margin + panel_w + gutter, margin + panel_h + gutter, width - margin, height - margin),
    ]
    for box, color in zip(boxes, colors):
        draw.rectangle(box, fill=color, outline="#111111", width=5)
    layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
    panels = _panel_boxes(width, height, margin, gutter)
    for panel, text, side in zip(
        panels,
        ["One last seed.", "Grow strong.", "Take your time.", "You made it."],
        ["left", "right", "left", "right"],
    ):
        _draw_bubble(
            layer, panel, text, side, 48, 20, 30, 28, 4,
            "#FFFFFF", "#111111", "#111111", "DejaVuSans.ttf",
            45, 42, 22, 26,
        )
    output = Image.alpha_composite(page.convert("RGBA"), layer).convert("RGB")
    output.save(Path(__file__).parent / "test_output.png")
    mask = np.asarray(layer.getchannel("A"), dtype=np.float32) / 255.0
    assert output.size == (width, height)
    assert mask.shape == (height, width)
    assert float(mask.max()) > 0.9
    print("PASS", output.size, mask.shape)


if __name__ == "__main__":
    main()
