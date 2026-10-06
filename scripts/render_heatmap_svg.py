import os
import sys
import json
from datetime import datetime

PALETTE = [
    "#161b22",  # Level 0 (None)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
    "#69f0a0"   # Level 5 (Neon top end for peak activity)
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def render_heatmap_svg(data_path="data/contributions.json", output_path="contrib-heatmap.svg"):
    if not os.path.exists(data_path):
        print(f"  [!] '{data_path}' not found. Running fetch_contributions.py first...")
        from fetch_contributions import fetch_contributions
        fetch_contributions()

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contribs = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    username = data.get("username", "krishnnavarun")

    box_size = 11.5
    gap = 3.5
    step = box_size + gap

    margin_left = 45
    margin_top = 70
    
    svg_w = 860
    svg_h = 230
    header_h = 36

    rect_elements = []
    month_labels = []
    last_month = None

    # Organize days into weeks (columns of 7 days)
    # Ensure we have 53 weeks
    weeks = []
    current_week = []
    for d in days:
        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    if current_week:
        weeks.append(current_week)

    # Cut/pad to exactly 53 weeks
    weeks = weeks[-53:]

    for w_idx, week in enumerate(weeks):
        x = margin_left + (w_idx * step)
        
        # Check month label
        if week:
            first_day_date = datetime.strptime(week[0]["date"], "%Y-%m-%d")
            m = first_day_date.month
            if m != last_month and w_idx > 0 and w_idx < 50:
                month_name = MONTH_NAMES[m - 1]
                month_labels.append(f'<text x="{x}" y="{margin_top - 10}" class="label">{month_name}</text>')
                last_month = m

        for d_idx, day_info in enumerate(week):
            y = margin_top + (d_idx * step)
            
            count = day_info.get("count", 0)
            level = day_info.get("level", 0)
            
            # Bright top level for high counts
            if count >= 12 and level >= 4:
                level = 5
            elif level > 4:
                level = 4
            elif level < 0:
                level = 0
            
            color = PALETTE[level]

            # Diagonal slide-down stagger calculation
            delay = round((w_idx * 0.015) + (d_idx * 0.03), 3)

            rect_elements.append(
                f'    <rect x="{x}" y="{y}" width="{box_size}" height="{box_size}" rx="2.5" fill="{color}" '
                f'style="animation: boxSlideDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) {delay}s both;">'
                f'<title>{count} contributions on {day_info.get("date")}</title></rect>'
            )

    rects_str = "\n".join(rect_elements)
    months_str = "\n".join(month_labels)

    # Day labels on the left (Mon, Wed, Fri)
    day_labels = [
        f'<text x="{margin_left - 12}" y="{margin_top + (1 * step) + 9}" text-anchor="end" class="label">Mon</text>',
        f'<text x="{margin_left - 12}" y="{margin_top + (3 * step) + 9}" text-anchor="end" class="label">Wed</text>',
        f'<text x="{margin_left - 12}" y="{margin_top + (5 * step) + 9}" text-anchor="end" class="label">Fri</text>'
    ]
    day_labels_str = "\n".join(day_labels)

    # Less -> More legend at bottom right
    legend_x = svg_w - 150
    legend_y = svg_h - 22
    legend_boxes = []
    for i, col in enumerate(PALETTE):
        legend_boxes.append(f'<rect x="{legend_x + (i * 14)}" y="{legend_y - 9}" width="10" height="10" rx="2" fill="{col}" />')
    legend_str = (
        f'<text x="{legend_x - 32}" y="{legend_y}" class="label">Less</text>' +
        "".join(legend_boxes) +
        f'<text x="{legend_x + (len(PALETTE) * 14) + 6}" y="{legend_y}" class="label">More</text>'
    )

    # Footer stats on bottom left
    footer_text = f"{total_contribs:,} contributions in the last year • {current_streak} day streak (best: {longest_streak} days)"
    footer_str = f'<text x="{margin_left}" y="{legend_y}" class="stats-footer">{footer_text}</text>'

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="860" height="{int(860 * (svg_h / svg_w))}">
  <style>
    @keyframes boxSlideDown {{
      0% {{ opacity: 0; transform: translateY(-12px) scale(0.4); }}
      100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    .bg {{ fill: #0d1117; rx: 10px; ry: 10px; stroke: #30363d; stroke-width: 1.5px; }}
    .header-bar {{ fill: #161b22; rx: 10px; ry: 10px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title {{ font-family: 'Fira Code', 'Consolas', monospace; font-size: 12px; fill: #39d353; font-weight: 600; }}
    .title-cmd {{ fill: #c9d1d9; }}
    .title-host {{ fill: #58a6ff; }}

    .label {{
      font-family: 'Fira Code', 'Consolas', 'Segoe UI', sans-serif;
      font-size: 10px;
      fill: #8b949e;
    }}
    .stats-footer {{
      font-family: 'Fira Code', 'Consolas', monospace;
      font-size: 11px;
      font-weight: 600;
      fill: #c9d1d9;
    }}
  </style>

  <!-- Background -->
  <rect width="{svg_w}" height="{svg_h}" class="bg" />

  <!-- Terminal Header -->
  <path d="M 0 0 h {svg_w} v {header_h} h -{svg_w} Z" class="header-bar" />
  <circle cx="20" cy="18" r="5" class="dot-red" />
  <circle cx="36" cy="18" r="5" class="dot-yellow" />
  <circle cx="52" cy="18" r="5" class="dot-green" />
  <text x="72" y="22" class="title">
    <tspan class="title-host">{username}@github</tspan> ~ $ <tspan class="title-cmd">./contributions.sh</tspan>
  </text>

  <!-- Month & Day Labels -->
{months_str}
{day_labels_str}

  <!-- Contribution Box Grid -->
  <g>
{rects_str}
  </g>

  <!-- Legend & Stats Footer -->
  <g>
    {footer_str}
    {legend_str}
  </g>
</svg>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"  [✓] Successfully rendered animated contribution heatmap SVG: '{output_path}'")

if __name__ == "__main__":
    render_heatmap_svg()
