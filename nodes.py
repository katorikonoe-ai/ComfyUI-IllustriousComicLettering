import math
from pathlib import Path

import numpy as np
try:
    import torch
except ImportError:  # Allows Pillow-only layout tests outside a ComfyUI runtime.
    torch = None
from PIL import Image, ImageColor, ImageDraw, ImageFont


def _tensor_to_pil(image):
    array = np.clip(image.detach().cpu().numpy() * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(array).convert("RGBA")


def _pil_to_tensor(image):
    if torch is None:
        raise RuntimeError("Torch is required when this node runs inside ComfyUI.")
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    return torch.from_numpy(array)


def _load_font(size, font_name=""):
    candidates = []
    if font_name.strip():
        candidates.append(font_name.strip())
    candidates.extend(
        [
            "DejaVuSans-Bold.ttf",
            "Arial Bold.ttf",
            "arialbd.ttf",
            "LiberationSans-Bold.ttf",
            "DejaVuSans.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _line_width(draw, text, font):
    box = draw.textbbox((0, 0), text or " ", font=font)
    return max(1, box[2] - box[0])


def _wrap(draw, text, font, max_width):
    result = []
    paragraphs = (text or "").strip().splitlines() or [""]
    for paragraph in paragraphs:
        words = paragraph.split()
        if not words:
            result.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if _line_width(draw, candidate, font) <= max_width:
                line = candidate
            else:
                result.append(line)
                line = word
        result.append(line)
    return result


def _fit_text(draw, text, requested_size, minimum_size, max_width, max_height, spacing_ratio, font_name):
    for size in range(requested_size, minimum_size - 1, -1):
        font = _load_font(size, font_name)
        lines = _wrap(draw, text, font, max_width)
        sample = draw.textbbox((0, 0), "Ag", font=font)
        line_height = max(1, sample[3] - sample[1])
        spacing = max(1, round(size * spacing_ratio))
        height = line_height * len(lines) + spacing * max(0, len(lines) - 1)
        width = max((_line_width(draw, line, font) for line in lines), default=1)
        if width <= max_width and height <= max_height:
            return font, lines, width, height, line_height, spacing
    font = _load_font(minimum_size, font_name)
    lines = _wrap(draw, text, font, max_width)
    sample = draw.textbbox((0, 0), "Ag", font=font)
    line_height = max(1, sample[3] - sample[1])
    spacing = max(1, round(minimum_size * spacing_ratio))
    height = line_height * len(lines) + spacing * max(0, len(lines) - 1)
    width = max((_line_width(draw, line, font) for line in lines), default=1)
    return font, lines, width, height, line_height, spacing


def _panel_boxes(width, height, outer_margin, gutter):
    usable_w = width - outer_margin * 2 - gutter
    usable_h = height - outer_margin * 2 - gutter
    left_w = usable_w // 2
    top_h = usable_h // 2
    return [
        (outer_margin, outer_margin, outer_margin + left_w, outer_margin + top_h),
        (outer_margin + left_w + gutter, outer_margin, width - outer_margin, outer_margin + top_h),
        (outer_margin, outer_margin + top_h + gutter, outer_margin + left_w, height - outer_margin),
        (outer_margin + left_w + gutter, outer_margin + top_h + gutter, width - outer_margin, height - outer_margin),
    ]


def _draw_bubble(layer, panel, text, speaker_side, font_size, min_font_size, padding,
                 panel_safe_margin, border_width, fill, outline, text_color, font_name,
                 bubble_width_limit=45, tail_length=42, tail_width=22,
                 bubble_top_offset=26):
    if not (text or "").strip():
        return
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = panel
    panel_w, panel_h = x1 - x0, y1 - y0
    width_ratio = min(90, max(20, bubble_width_limit)) / 100.0
    max_bubble_w = max(80, min(panel_w - panel_safe_margin * 2, int(panel_w * width_ratio)))
    max_text_w = max(40, max_bubble_w - padding * 2)
    max_text_h = max(50, int(panel_h * 0.28) - padding * 2)
    font, lines, text_w, text_h, line_h, line_spacing = _fit_text(
        draw, text, font_size, min_font_size, max_text_w, max_text_h, 0.16, font_name
    )
    bubble_w = min(max_bubble_w, text_w + padding * 2)
    bubble_h = min(panel_h - panel_safe_margin * 2, text_h + padding * 2)

    # Place the bubble opposite the speaker so it does not cover the face.
    if speaker_side == "left":
        bx = x1 - panel_safe_margin - bubble_w
        tail_x = x0 + int(panel_w * 0.32)
    elif speaker_side == "right":
        bx = x0 + panel_safe_margin
        tail_x = x0 + int(panel_w * 0.68)
    else:
        bx = x0 + (panel_w - bubble_w) // 2
        tail_x = x0 + panel_w // 2
    max_by = max(y0, y1 - panel_safe_margin - bubble_h)
    by = min(max_by, y0 + bubble_top_offset)
    box = (bx, by, bx + bubble_w, by + bubble_h)

    draw.ellipse(box, fill=fill, outline=outline, width=border_width)
    center_x = bx + bubble_w / 2
    center_y = by + bubble_h / 2
    target_y = min(y1 - panel_safe_margin, by + bubble_h + max(1, tail_length))
    angle = math.atan2(target_y - center_y, tail_x - center_x)
    radius_x, radius_y = bubble_w / 2, bubble_h / 2
    def edge(a):
        scale = 1.0 / math.sqrt((math.cos(a) / radius_x) ** 2 + (math.sin(a) / radius_y) ** 2)
        return center_x + math.cos(a) * scale, center_y + math.sin(a) * scale
    edge_x, edge_y = edge(angle)
    direction_x, direction_y = math.cos(angle), math.sin(angle)
    tip_x = edge_x + direction_x * tail_length
    tip_y = edge_y + direction_y * tail_length
    tip_x = min(x1 - panel_safe_margin, max(x0 + panel_safe_margin, tip_x))
    tip_y = min(y1 - panel_safe_margin, max(y0 + panel_safe_margin, tip_y))
    half_width = tail_width / 2.0
    tangent_x, tangent_y = -direction_y, direction_x
    p1 = (edge_x + tangent_x * half_width, edge_y + tangent_y * half_width)
    p2 = (edge_x - tangent_x * half_width, edge_y - tangent_y * half_width)
    draw.polygon([p1, (tip_x, tip_y), p2], fill=fill)
    if border_width:
        draw.line([p1, (tip_x, tip_y), p2], fill=outline, width=border_width, joint="curve")

    cursor_y = by + (bubble_h - text_h) / 2
    for line in lines:
        bounds = draw.textbbox((0, 0), line or " ", font=font)
        width = bounds[2] - bounds[0]
        draw.text(
            (bx + (bubble_w - width) / 2, cursor_y - bounds[1]),
            line,
            font=font,
            fill=text_color,
        )
        cursor_y += line_h + line_spacing


class IllustriousComicLettering4Panel:
    """Deterministic lettering for a fixed 2x2 comic page."""

    @classmethod
    def INPUT_TYPES(cls):
        sides = ["left", "right", "center"]
        return {
            "required": {
                "image": ("IMAGE",),
                "panel_1_text": ("STRING", {"default": "One last seed.", "multiline": True}),
                "panel_2_text": ("STRING", {"default": "Grow strong.", "multiline": True}),
                "panel_3_text": ("STRING", {"default": "Take your time.", "multiline": True}),
                "panel_4_text": ("STRING", {"default": "You made it.", "multiline": True}),
                "panel_1_speaker": (sides,),
                "panel_2_speaker": (sides,),
                "panel_3_speaker": (sides,),
                "panel_4_speaker": (sides,),
                "font_size": ("INT", {"default": 42, "min": 12, "max": 180}),
                "min_font_size": ("INT", {"default": 20, "min": 8, "max": 96}),
                "padding": ("INT", {"default": 28, "min": 4, "max": 160}),
                "outer_margin": ("INT", {"default": 45, "min": 0, "max": 512}),
                "gutter": ("INT", {"default": 24, "min": 0, "max": 256}),
                "panel_safe_margin": ("INT", {"default": 26, "min": 0, "max": 256}),
                "border_width": ("INT", {"default": 4, "min": 0, "max": 24}),
                "fill_color": ("STRING", {"default": "#FFFFFF"}),
                "border_color": ("STRING", {"default": "#111111"}),
                "text_color": ("STRING", {"default": "#111111"}),
                "font_name": ("STRING", {"default": "DejaVuSans.ttf"}),
                "bubble_width_limit": ("INT", {"default": 45, "min": 20, "max": 90,
                                                "tooltip": "Maximum bubble width as a percentage of panel width."}),
                "tail_length": ("INT", {"default": 42, "min": 0, "max": 240}),
                "tail_width": ("INT", {"default": 22, "min": 4, "max": 120}),
                "bubble_top_offset": ("INT", {"default": 26, "min": 0, "max": 512,
                                              "tooltip": "Distance from the top of each panel in pixels."}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("lettered_page", "bubble_mask")
    FUNCTION = "render"
    CATEGORY = "Illustrious Comic/Lettering"

    def render(self, image, panel_1_text, panel_2_text, panel_3_text, panel_4_text,
               panel_1_speaker, panel_2_speaker, panel_3_speaker, panel_4_speaker,
               font_size, min_font_size, padding, outer_margin, gutter,
               panel_safe_margin, border_width, fill_color, border_color,
               text_color, font_name, bubble_width_limit=45, tail_length=42,
               tail_width=22, bubble_top_offset=26):
        output, masks = [], []
        fill = ImageColor.getcolor(fill_color, "RGBA")
        outline = ImageColor.getcolor(border_color, "RGBA")
        color = ImageColor.getcolor(text_color, "RGBA")
        texts = [panel_1_text, panel_2_text, panel_3_text, panel_4_text]
        sides = [panel_1_speaker, panel_2_speaker, panel_3_speaker, panel_4_speaker]
        for sample in image:
            base = _tensor_to_pil(sample)
            layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
            panels = _panel_boxes(base.width, base.height, outer_margin, gutter)
            for panel, text, side in zip(panels, texts, sides):
                _draw_bubble(
                    layer, panel, text, side, font_size, min_font_size, padding,
                    panel_safe_margin, border_width, fill, outline, color, font_name,
                    bubble_width_limit, tail_length, tail_width, bubble_top_offset,
                )
            composed = Image.alpha_composite(base, layer)
            output.append(_pil_to_tensor(composed))
            alpha = np.asarray(layer.getchannel("A"), dtype=np.float32) / 255.0
            masks.append(torch.from_numpy(alpha))
        return torch.stack(output), torch.stack(masks)


NODE_CLASS_MAPPINGS = {
    "IllustriousComicLettering4Panel": IllustriousComicLettering4Panel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IllustriousComicLettering4Panel": "Illustrious Comic Lettering - 4 Panel",
}
