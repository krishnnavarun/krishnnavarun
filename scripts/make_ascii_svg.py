import os
import sys
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # Bright (sparse) -> Dark (dense)

def generate_procedural_ascii_grid(cols=84, rows=48):
    """Generates a stylish procedural fallback ASCII portrait grid if no source image is provided."""
    import math
    grid = []
    for r in range(rows):
        line = []
        ny = (r / rows - 0.5) * 2.2
        for c in range(cols):
            nx = (c / cols - 0.5) * 2.2
            # Head / Silhouette distance field shape
            dist_head = math.sqrt((nx * 1.1)**2 + (ny + 0.2)**2)
            dist_shoulders = math.sqrt((nx * 0.7)**2 + (ny - 0.8)**2)
            
            # Combine shapes
            val = 0.0
            if dist_head < 0.55:
                # Face features noise/shading
                shade = (1.0 - dist_head / 0.55)
                # Add synthetic eye & shadow contours
                if -0.2 < ny < -0.05 and abs(nx) < 0.3:
                    shade += 0.35
                val = max(val, shade)
            elif dist_shoulders < 0.85 and ny > 0.1:
                val = max(val, 0.45 * (1.0 - dist_shoulders / 0.85))

            idx = int(val * (len(RAMP) - 1))
            idx = max(0, min(len(RAMP) - 1, idx))
            line.append(RAMP[idx])
        grid.append("".join(line))
    return grid

def image_to_ascii(image_path, cols=84, aspect_ratio=0.5):
    """Converts image file to grid of ASCII characters based on brightness."""
    img = Image.open(image_path).convert('L')
    orig_w, orig_h = img.size
    rows = int(cols * (orig_h / orig_w) * aspect_ratio)
    img_resized = img.resize((cols, rows), Image.Resampling.LANCZOS)

    grid = []
    for y in range(rows):
        line = []
        for x in range(cols):
            pixel = img_resized.getpixel((x, y))
            # 255 = Bright (Space), 0 = Dark (Dense Glyph)
            brightness = pixel / 255.0
            ramp_idx = int((1.0 - brightness) * (len(RAMP) - 1))
            ramp_idx = max(0, min(len(RAMP) - 1, ramp_idx))
            line.append(RAMP[ramp_idx])
        grid.append("".join(line))
    return grid, cols, rows

def build_ascii_svg(ascii_lines, output_file="avi-ascii.svg"):
    cols = max(len(line) for line in ascii_lines)
    rows = len(ascii_lines)

    char_w = 7.2
    char_h = 13.0
    padding_x = 20
    padding_y = 25
    header_h = 35

    svg_w = int(cols * char_w + padding_x * 2)
    svg_h = int(rows * char_h + padding_y * 2 + header_h)

    # Escape HTML special characters for SVG text nodes
    def escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&#160;")

    # Generate row-by-row SVG clip-path SMIL animations
    clip_paths = []
    text_elements = []
    cursors = []

    total_duration = 2.5 # Total typing duration in seconds
    row_delay = total_duration / rows

    for r, line in enumerate(ascii_lines):
        y_pos = header_h + padding_y + (r * char_h)
        clip_id = f"clip-row-{r}"
        start_time = round(r * row_delay, 3)
        row_dur = round(row_delay * 1.5, 3)

        # Clip path rectangle expanding x from 0 to max width
        clip_paths.append(f'''    <clipPath id="{clip_id}">
      <rect x="0" y="{y_pos - 10}" width="0" height="{char_h + 2}">
        <animate attributeName="width" from="0" to="{svg_w}" begin="{start_time}s" dur="{row_dur}s" fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1.0"/>
      </rect>
    </clipPath>''')

        escaped_line = escape_xml(line)
        text_elements.append(f'''    <text x="{padding_x}" y="{y_pos}" clip-path="url(#{clip_id})" class="ascii-row">{escaped_line}</text>''')

    clip_paths_str = "\n".join(clip_paths)
    text_elements_str = "\n".join(text_elements)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="370" height="{int(370 * (svg_h / svg_w))}">
  <style>
    .bg {{ fill: #0d1117; rx: 10px; ry: 10px; stroke: #30363d; stroke-width: 1.5px; }}
    .header-bar {{ fill: #161b22; rx: 10px; ry: 10px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title {{ font-family: 'Fira Code', 'Consolas', 'Monaco', monospace; font-size: 12px; fill: #8b949e; font-weight: 600; }}
    .ascii-row {{
      font-family: 'Fira Code', 'Cascadia Code', 'Consolas', 'Courier New', monospace;
      font-size: 10px;
      fill: #58a6ff;
      white-space: pre;
      letter-spacing: 0px;
    }}
  </style>

  <defs>
{clip_paths_str}
  </defs>

  <!-- Container background -->
  <rect width="{svg_w}" height="{svg_h}" class="bg" />
  
  <!-- Terminal Header -->
  <path d="M 0 0 h {svg_w} v 36 h -{svg_w} Z" class="header-bar" />
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />
  <text x="{svg_w / 2}" y="22" text-anchor="middle" class="title">portrait.ascii</text>

  <!-- ASCII Portrait Content -->
  <g>
{text_elements_str}
  </g>
</svg>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  [✓] Successfully generated self-typing ASCII SVG: '{output_file}' ({cols}x{rows} grid)")

def main():
    prepped_path = "source-prepped.png"
    source_path = "source-photo.jpg"
    
    if os.path.exists(prepped_path):
        ascii_lines, c, r = image_to_ascii(prepped_path)
    elif os.path.exists(source_path):
        ascii_lines, c, r = image_to_ascii(source_path)
    else:
        print("  [!] No source photo found. Generating procedural ASCII portrait grid...")
        ascii_lines = generate_procedural_ascii_grid()
        
    build_ascii_svg(ascii_lines, "avi-ascii.svg")

if __name__ == "__main__":
    main()
