import os
import sys
import json
import re
from datetime import datetime, timedelta

def generate_fallback_contributions():
    """Generates synthetic initial contribution data for 53 weeks (371 days) if offline or initializing."""
    today = datetime.now().date()
    start_date = today - timedelta(days=364)
    
    days = []
    total_count = 0
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    max_day = 0

    # Deterministic pattern for aesthetic fallback heatmap
    for i in range(365):
        d = start_date + timedelta(days=i)
        date_str = d.isoformat()
        
        # Weekend activity vs weekday activity
        weekday = d.weekday()
        if (i % 7 in [1, 2, 3, 4]) and (i % 5 != 0):
            level = (i % 4) + 1
            count = level * 3 + (i % 5)
        elif (i % 13 == 0):
            level = 4
            count = 18
        else:
            level = 0
            count = 0

        total_count += count
        if count > max_day:
            max_day = count

        if count > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

        days.append({
            "date": date_str,
            "count": count,
            "level": level
        })

    current_streak = temp_streak

    return {
        "username": "krishnnavarun",
        "fetched_at": datetime.now().isoformat(),
        "total_contributions": total_count,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day_count": max_day,
        "days": days
    }

def fetch_contributions(username="krishnnavarun", output_path="data/contributions.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        import requests
        from bs4 import BeautifulSoup
        print(f"Fetching GitHub contributions for '{username}' from {url}...")
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code != 200:
            print(f"  [!] HTTP {resp.status_code} received from GitHub. Using generated fallback data.")
            data = generate_fallback_contributions()
            data["username"] = username
        else:
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Find calendar day cells
            # GitHub uses <td class="ContributionCalendar-day" data-date="2024-01-01" data-level="2" ...>
            # or <rect class="ContributionCalendar-day" data-date="..." data-level="...">
            day_cells = soup.find_all(['td', 'rect'], class_=re.compile(r'ContributionCalendar-day'))
            
            if not day_cells:
                # Alternate selector for tooltip matching
                day_cells = soup.select('[data-date]')

            if not day_cells:
                print("  [!] Could not parse day cells from HTML. Using generated fallback data.")
                data = generate_fallback_contributions()
                data["username"] = username
            else:
                days = []
                total_count = 0
                max_day = 0
                
                # Create map of tooltips if present (GitHub uses tool-tip elements for counts)
                tooltips = {}
                for tt in soup.find_all('tool-tip'):
                    for_id = tt.get('for', '')
                    if for_id:
                        tooltips[for_id] = tt.text.strip()

                for cell in day_cells:
                    date_str = cell.get('data-date')
                    if not date_str:
                        continue
                    
                    level_str = cell.get('data-level', '0')
                    try:
                        level = int(level_str)
                    except ValueError:
                        level = 0
                    
                    # Determine contribution count
                    count = 0
                    cell_id = cell.get('id', '')
                    tooltip_text = tooltips.get(cell_id, '')
                    
                    if tooltip_text:
                        match = re.search(r'(\d+)\s+contribution', tooltip_text)
                        if match:
                            count = int(match.group(1))
                    elif cell.get('data-count'):
                        count = int(cell.get('data-count'))
                    else:
                        # Estimate from level if exact count unavailable
                        count = level * 3 if level > 0 else 0

                    total_count += count
                    if count > max_day:
                        max_day = count

                    days.append({
                        "date": date_str,
                        "count": count,
                        "level": level
                    })

                # Sort by date
                days.sort(key=lambda d: d['date'])

                # Compute streaks
                temp_streak = 0
                longest_streak = 0
                current_streak = 0
                
                for d in days:
                    if d['count'] > 0:
                        temp_streak += 1
                        if temp_streak > longest_streak:
                            longest_streak = temp_streak
                    else:
                        temp_streak = 0
                
                # Current streak walking backwards from latest
                curr = 0
                for d in reversed(days):
                    if d['count'] > 0:
                        curr += 1
                    elif curr > 0:
                        break
                current_streak = curr

                data = {
                    "username": username,
                    "fetched_at": datetime.now().isoformat(),
                    "total_contributions": total_count,
                    "current_streak": current_streak,
                    "longest_streak": longest_streak,
                    "best_day_count": max_day,
                    "days": days
                }
                print(f"  [✓] Successfully parsed {len(days)} contribution days! Total: {total_count}")

    except Exception as e:
        print(f"  [!] Error fetching contributions ({e}). Using generated fallback data.")
        data = generate_fallback_contributions()
        data["username"] = username

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"  [✓] Saved contribution data to '{output_path}'")

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "krishnnavarun"
    fetch_contributions(user)
