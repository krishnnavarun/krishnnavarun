import sys
import os

# Add scripts directory to module path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_contributions import fetch_contributions
from render_heatmap_svg import render_heatmap_svg
from make_info_card import build_info_card_svg
from make_ascii_svg import main as make_ascii_main

def generate_all(username="krishnnavarun"):
    print(f"==================================================")
    print(f"  Generating GitHub Profile Art for '{username}'")
    print(f"==================================================")
    
    print("\n[1/4] Fetching GitHub contribution stats...")
    fetch_contributions(username)

    print("\n[2/4] Rendering contribution heatmap SVG...")
    render_heatmap_svg()

    print("\n[3/4] Building neofetch info card SVG...")
    build_info_card_svg()

    print("\n[4/4] Generating ASCII portrait SVG...")
    make_ascii_main()

    print("\n==================================================")
    print("  [✓] All 3 SVGs successfully generated and ready!")
    print("==================================================")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "krishnnavarun"
    generate_all(user)
