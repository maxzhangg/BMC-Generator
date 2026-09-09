import pandas as pd
import fitz  # PyMuPDF
from reportlab.lib.units import cm
import textwrap

# === 读取 Excel 数据 ===
df = pd.read_excel("VB.xlsx", header=None)
values = df.iloc[:, 0].astype(str).tolist()

if len(values) != 30:
    raise ValueError("Excel 中应为 30 行数据")

# === 直接以左下角为原点定义 box 坐标（x, y 是左下角，单位 pt） ===
boxes = [
    (10 * cm, 10 * cm, 16 * cm, 8.3 * cm),
    (26 * cm, 10 * cm, 16 * cm, 8.3 * cm),
    (42 * cm, 10 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 10 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 10 * cm, 16 * cm, 8.3 * cm),
    (10 * cm, 18 * cm, 16 * cm, 8.3 * cm),
    (26 * cm, 18 * cm, 16 * cm, 8.3 * cm),
    (42 * cm, 18 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 18 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 18 * cm, 16 * cm, 8.3 * cm),
    (10 * cm, 26 * cm, 16 * cm, 8.3 * cm),
    (26 * cm, 26 * cm, 16 * cm, 8.3 * cm),
    (42 * cm, 26 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 26 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 26 * cm, 16 * cm, 8.3 * cm),
    (1  * cm, 37 * cm, 30 * cm, 25 * cm),
    (31 * cm, 34 * cm, 10 * cm, 8.3 * cm),
    (42 * cm, 34 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 34 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 34 * cm, 16 * cm, 8.3 * cm),
    (10 * cm, 42 * cm, 16 * cm, 8.3 * cm),
    (31 * cm, 42 * cm, 10 * cm, 8.3 * cm),
    (42 * cm, 42 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 42 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 42 * cm, 16 * cm, 8.3 * cm),
    (10 * cm, 50 * cm, 16 * cm, 8.3 * cm),
    (31 * cm, 50 * cm, 10 * cm, 8.3 * cm),
    (42 * cm, 50 * cm, 16 * cm, 8.3 * cm),
    (58 * cm, 50 * cm, 16 * cm, 8.3 * cm),
    (74 * cm, 50 * cm, 16 * cm, 8.3 * cm),
]

# === 打开 PDF 页面 ===
doc = fitz.open("validation_board_3.6.2.pdf")
page = doc[0]

# === 写入函数：容错 + 自动换行版本 ===
def draw_wrapped_text_in_box(page, text, x, y, w, h,
                              max_font_size=20,
                              min_font_size=10,
                              max_lines=5,
                              line_spacing=1.1,
                              font_name="Times-Roman"):
    """在指定 box 内自动布局文字，支持换行与数字加大"""
    # 可选：灰色背景调试框
    page.draw_rect(fitz.Rect(x, y, x + w, y + h),fill=(0.95, 0.95, 0.95),color=(0.8, 0.8, 0.8))

    is_numeric = text.replace(".", "", 1).isdigit()

    # 纯数字 → 单行居中大字号
    if is_numeric and len(text) <= 15:
        page.insert_textbox(
            fitz.Rect(x, y, x + w, y + h),
            text,
            fontsize=max_font_size,
            fontname=font_name,
            color=(0, 0, 0),
            align=1,
            overlay=True
        )
        return

    # 自动换行逻辑
    font_size = max_font_size
    wrap_width = int(w / (font_size * 0.6))
    wrapped = textwrap.wrap(text, width=wrap_width)

    while ((len(wrapped) > max_lines or
            len(wrapped) * font_size * line_spacing > h)
           and font_size > min_font_size):
        font_size -= 1
        wrap_width = int(w / (font_size * 0.6))
        wrapped = textwrap.wrap(text, width=wrap_width)

    # 行数过多 → 截断
    if len(wrapped) > max_lines:
        wrapped = wrapped[:max_lines]
        wrapped[-1] = wrapped[-1][:max(0, len(wrapped[-1]) - 3)] + "..."

    # 垂直居中绘制
    total_height = len(wrapped) * font_size * line_spacing
    start_y = y + (h - total_height) / 2

    for i, line in enumerate(wrapped):
        rect = fitz.Rect(
            x,
            start_y + (len(wrapped) - 1 - i) * font_size * line_spacing,
            x + w,
            start_y + (len(wrapped) - i) * font_size * line_spacing,
        )
        page.insert_textbox(
            rect,
            line,
            fontsize=font_size,
            fontname=font_name,
            color=(0, 0, 0),
            align=1,
            overlay=True
        )

# === 写入所有内容 ===
for value, (x, y, w, h) in zip(values, boxes):
    draw_wrapped_text_in_box(page, value, x, y, w, h)

# === 保存 PDF ===
doc.save("validation_board_filled_FINAL.pdf")
doc.close()

print("✅ 成功生成：validation_board_filled_FINAL.pdf")
