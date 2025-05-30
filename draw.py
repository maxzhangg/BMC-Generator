# -*- coding: utf-8 -*-

from PIL import Image, ImageDraw, ImageFont
import pandas as pd

print("BMC Generator - Developed by Max Zhang for GNG4120/GNG5120")

# ========= 参数配置 =========
canvas_width, canvas_height = 1450, 850
excel_path = "BMC.xlsx"
font_content_size = 14
output_prefix = "bmc_"

# ========= 字体设置 =========
try:
    font_title = ImageFont.truetype("arial.ttf", size=18)
    font_content = ImageFont.truetype("arial.ttf", size=font_content_size)
except IOError:
    font_title = ImageFont.load_default()
    font_content = ImageFont.load_default()

# ========= 留白与 block 比例 =========
blank_ratio = 0.01
blank_x = blank_ratio
blank_y = blank_ratio * canvas_width / canvas_height
rec_x, rec_y = 0.2, 0.71
block_ratios = {
    "Key Partnerships":      (blank_x, blank_y, rec_x, rec_y),
    "Key Activities":        (rec_x * (1 - blank_x * 2) + blank_x, blank_y, rec_x, rec_y / 2),
    "Key Resources":         (rec_x * (1 - blank_x * 2) + blank_x, rec_y / 2 * (1 - blank_y * 2) + blank_y, rec_x, rec_y / 2),
    "Value Propositions":    (rec_x * 2 * (1 - blank_x * 2) + blank_x, blank_y, rec_x, rec_y),
    "Customer Relationships":(rec_x * 3 * (1 - blank_x * 2) + blank_x, blank_y, rec_x, rec_y / 2),
    "Channels":              (rec_x * 3 * (1 - blank_x * 2) + blank_x, rec_y / 2 * (1 - blank_y * 2) + blank_y, rec_x, rec_y / 2),
    "Customer Segments":     (rec_x * 4 * (1 - blank_x * 2) + blank_x, blank_y, rec_x, rec_y),
    "Cost Structure":        (blank_x, rec_y * (1 - blank_y * 2) + blank_y, 0.5, 1 - rec_y),
    "Revenue Streams":       (0.5 * (1 - blank_x * 2) + blank_x, rec_y * (1 - blank_y * 2) + blank_y, 0.5, 1 - rec_y)
}

# ========= 颜色映射 =========
color_map = {
    "Baseline": "#FFD700",
    "Health Check": "#FF6347",
    "Assumptions": "#87CEFA"
}

# ========= 主绘图逻辑 =========
def draw_text_blocks(draw, df_filtered, block_name, x, y, w, h):
    is_bottom = block_name in ["Cost Structure", "Revenue Streams"]
    max_per_col = 6
    box_width = int(w * 0.3)
    box_height = int(font_content_size * 1.8) + 4
    col_margin_x = 20
    row_margin_y = 10

    if is_bottom:
        box_width = int(w * 0.3)
        col_margin_x = 20
        row_margin_y = 10
        start_x = x + 10
        start_y = y + 40
        current_col = 0
        current_y = start_y
        line_spacing = int(font_content_size * 1.4)

        for _, row in df_filtered.iterrows():
            cls, text = row["Class"], str(row["Content"])
            color = color_map.get(cls, "#DDDDDD")
            ascii_text = ''.join([ch if ord(ch) < 128 else '?' for ch in text])
            words = ascii_text.strip().split(' ')
            lines, current_line = [], ""
            for word in words:
                test_line = (current_line + " " + word) if current_line else word
                test_w = font_content.getbbox(test_line)[2] - font_content.getbbox(test_line)[0]
                if test_w < box_width - 10:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            box_height = line_spacing * len(lines) + 4
            if current_y + box_height > y + h:
                current_col += 1
                current_y = start_y
            cx = start_x + current_col * (box_width + col_margin_x)
            cy = current_y
            draw.rectangle([cx, cy, cx + box_width, cy + box_height], fill=color, outline="black")
            for i, line in enumerate(lines):
                draw.text((cx + 5, cy + 4 + i * line_spacing), line, fill="black", font=font_content)
            current_y += box_height + row_margin_y

    else:
        text_y = y + 40
        line_spacing = int(font_content_size * 1.4)
        for _, row in df_filtered.iterrows():
            cls, text = row["Class"], row["Content"]
            color = color_map.get(cls, "#DDDDDD")

            ascii_text = ''.join([ch if ord(ch) < 128 else '?' for ch in str(text)])
            words = ascii_text.split(' ')
            lines, current_line = [], ""
            for word in words:
                test_line = (current_line + " " + word) if current_line else word
                text_width = font_content.getbbox(test_line)[2] - font_content.getbbox(test_line)[0]
                if text_width < w - 40:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            box_height = line_spacing * len(lines)
            if text_y + box_height > y + h:
                break
            draw.rectangle([x + 10, text_y, x + w - 10, text_y + box_height], fill=color, outline="black")
            for i, line in enumerate(lines):
                draw.text((x + 15, text_y + i * line_spacing + 2), line, fill="black", font=font_content)
            text_y += box_height + 10

# ========= 封装完整绘图函数 =========
def draw_bmc(classes_to_include, output_filename):
    df = pd.read_excel(excel_path)
    df = df[df["Class"].isin(classes_to_include)]

    img = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(img)

    for block, (x_r, y_r, w_r, h_r) in block_ratios.items():
        x = int(x_r * canvas_width)
        y = int(y_r * canvas_height)
        w = int(w_r * canvas_width * (1 - blank_x * 2))
        h = int(h_r * canvas_height * (1 - blank_y * 2))
        draw.rectangle([x, y, x + w, y + h], outline="black", width=2)
        draw.text((x + 10, y + 10), block, fill="black", font=font_title)
        df_block = df[df["Block"] == block]
        if not df_block.empty:
            draw_text_blocks(draw, df_block, block, x, y, w, h)

    img.save(output_filename)
    print(f"Saved：{output_filename}")

# ========= 生成三张图 =========
draw_bmc(["Baseline"], output_prefix + "baseline.png")
draw_bmc(["Baseline", "Health Check"], output_prefix + "baseline_health.png")
draw_bmc(["Baseline", "Health Check", "Assumptions"], output_prefix + "baseline_health_assumptions.png")
