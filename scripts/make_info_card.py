import os
import sys

def build_info_card_svg(output_path="info-card.svg"):
    is_static = os.environ.get("STATIC", "0") == "1"

    # Terminal card details
    username = "krishnnavarun"
    host = "github"
    prompt = f"{username}@{host} ~ $ neofetch"
    
    rows = [
        ("OS", "GitHub Profile OS x86_64"),
        ("Host", "Full-Stack & Systems Developer"),
        ("Uptime", "Coding daily since 2022"),
        ("Now", "Building AI Agents, CLI Tools & Interactive SVGs"),
        ("Prev", "Full-Stack Development, Algorithmic Problem Solving"),
        ("Stack", "Python, TypeScript, React, Next.js, Node.js, C++"),
        ("Highlights", "Daily Cron Automated READMEs • Clean Code • Open Source"),
        ("Terminal", "zsh 5.9 (x86_64-apple-darwin22.0)"),
        ("Palette", "■ ■ ■ ■ ■ ■ ■ ■")
    ]

    card_w = 520
    card_h = 360
    header_h = 36
    padding_x = 24
    start_y = 65
    line_h = 30

    row_elements = []
    
    for idx, (key, value) in enumerate(rows):
        y_pos = start_y + (idx * line_h)
        delay = round(0.1 + (idx * 0.1), 2)
        
        anim_style = "" if is_static else f"animation: slideFadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) {delay}s both;"

        if key == "Palette":
            palette_colors = ["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39d353", "#79c0ff", "#d2a8ff"]
            spans = "".join([f'<tspan fill="{c}">■ </tspan>' for c in palette_colors])
            row_elements.append(f'''    <g style="{anim_style}">
      <text x="{padding_x}" y="{y_pos}" class="card-key">{key}:</text>
      <text x="{padding_x + 95}" y="{y_pos}" class="card-val">{spans}</text>
    </g>''')
        else:
            row_elements.append(f'''    <g style="{anim_style}">
      <text x="{padding_x}" y="{y_pos}" class="card-key">{key}:</text>
      <text x="{padding_x + 95}" y="{y_pos}" class="card-val">{value}</text>
    </g>''')

    rows_str = "\n".join(row_elements)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_w} {card_h}" width="490" height="{int(490 * (card_h / card_w))}">
  <style>
    @keyframes slideFadeIn {{
      0% {{ opacity: 0; transform: translateY(8px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}

    .bg {{ fill: #0d1117; rx: 10px; ry: 10px; stroke: #30363d; stroke-width: 1.5px; }}
    .header-bar {{ fill: #161b22; rx: 10px; ry: 10px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .prompt {{ font-family: 'Fira Code', 'Consolas', monospace; font-size: 12px; fill: #39d353; font-weight: 600; }}
    .prompt-host {{ fill: #58a6ff; }}
    .prompt-path {{ fill: #bc8cff; }}
    .prompt-cmd {{ fill: #c9d1d9; }}
    
    .card-key {{
      font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
      font-size: 12.5px;
      font-weight: 700;
      fill: #58a6ff;
    }}
    .card-val {{
      font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
      font-size: 12px;
      fill: #c9d1d9;
    }}
  </style>

  <!-- Card Background -->
  <rect width="{card_w}" height="{card_h}" class="bg" />

  <!-- Terminal Header Bar -->
  <path d="M 0 0 h {card_w} v {header_h} h -{card_w} Z" class="header-bar" />
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />

  <!-- Terminal Prompt Title -->
  <text x="72" y="22" class="prompt">
    <tspan class="prompt-host">{username}@{host}</tspan>:<tspan class="prompt-path">~</tspan>$ <tspan class="prompt-cmd">neofetch</tspan>
  </text>

  <!-- Info Key-Values -->
  <g>
{rows_str}
  </g>
</svg>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  [✓] Successfully generated info-card SVG: '{output_path}'")

if __name__ == "__main__":
    build_info_card_svg()
