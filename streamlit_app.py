import streamlit as st
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import pandas as pd
import math
import os

st.set_page_config(page_title="Smash Bracket", page_icon="🎮", layout="wide")

# --- Smash Ultimate Character List (for use in data entry and info page) ---
# NOTE: This list is slightly smaller than the full list to match the provided data's scope.
SMASH_CHARACTERS = [
    "Mario", "Donkey Kong", "Link", "Samus", "Dark Samus", "Yoshi", "Kirby", "Fox", 
    "Pikachu", "Luigi", "Ness", "Captain Falcon", "Jigglypuff", "Peach", "Daisy", 
    "Bowser", "Ice Climbers", "Sheik", "Zelda", "Dr. Mario", "Pichu", "Falco", 
    "Marth", "Lucina", "Young Link", "Ganondorf", "Mewtwo", "Roy", "Chrom", 
    "Mr. Game & Watch", "Meta Knight", "Pit", "Dark Pit", "Zero Suit Samus", 
    "Wario", "Snake", "Ike", "Pokémon Trainer", "Diddy Kong", "Lucas", "Sonic", 
    "King Dedede", "Olimar", "Lucario", "R.O.B.", "Toon Link", "Wolf", "Villager", 
    "Mega Man", "Wii Fit Trainer", "Rosalina & Lumal", "Little Mac", "Greninja", 
    "Palutena", "Pac-Man", "Robin", "Shulk", "Bowser Jr.", "Duck Hunt", "Ryu", 
    "Ken", "Cloud", "Corrin", "Bayonetta", "Inkling", "Ridley", "Simon", "Richter", 
    "King K. Rool", "Isabelle", "Incineroar", "Piranha Plant", "Joker", "Hero", 
    "Banjo & Kazooie", "Terry Bogard", "Byleth", "Min Min", "Steve", "Sephiroth", 
    "Pyra/Mythra", "Kazuya", "Sora", "Mii Brawler", "Mii Swordfighter", "Mii Gunner"
]

# --- ACTUAL CHARACTER DATA FROM UPLOADED PDF ---
# This dictionary replaces the random mock data generator.
SMASH_DATA = {
    "Mario": {"Tier Rank (S-F)": "B", "Weight": 98, "Run Speed": 1.57, "Air Speed": 0.9, "Fall Speed": 1.62},
    "Donkey Kong": {"Tier Rank (S-F)": "B", "Weight": 127, "Run Speed": 1.65, "Air Speed": 0.95, "Fall Speed": "Close Combat"},
    "Link": {"Tier Rank (S-F)": "B", "Weight": 104, "Run Speed": 1.43, "Air Speed": 0.95, "Fall Speed": 1.62},
    "Samus": {"Tier Rank (S-F)": "B", "Weight": 108, "Run Speed": 1.51, "Air Speed": 0.98, "Fall Speed": "Charge Shot, Missile, Screw"},
    "Dark Samus": {"Tier Rank (S-F)": "B", "Weight": 108, "Run Speed": 1.51, "Air Speed": 0.98, "Fall Speed": "Attack, Bomb, Phazon Laser"},
    "Yoshi": {"Tier Rank (S-F)": "B", "Weight": 104, "Run Speed": 1.48, "Air Speed": 1.3, "Fall Speed": 1.29},
    "Kirby": {"Tier Rank (S-F)": "C", "Weight": 79, "Run Speed": 1.25, "Air Speed": 1.1, "Fall Speed": 1.2},
    "Fox": {"Tier Rank (S-F)": "S", "Weight": 77, "Run Speed": 2.08, "Air Speed": 1.2, "Fall Speed": 1.8},
    "Pikachu": {"Tier Rank (S-F)": "S", "Weight": 68, "Run Speed": 2.04, "Air Speed": 1.05, "Fall Speed": "Close Combat"},
    "Luigi": {"Tier Rank (S-F)": "B", "Weight": 97, "Run Speed": 1.37, "Air Speed": 0.98, "Fall Speed": 1.5},
    "Ness": {"Tier Rank (S-F)": "B", "Weight": 94, "Run Speed": 1.45, "Air Speed": 0.98, "Fall Speed": 1.5},
    "Captain Falcon": {"Tier Rank (S-F)": "A", "Weight": 104, "Run Speed": 2.55, "Air Speed": 1.15, "Fall Speed": 1.7},
    "Jigglypuff": {"Tier Rank (S-F)": "D", "Weight": 60, "Run Speed": 1.07, "Air Speed": 0.7, "Fall Speed": 1.1},
    "Peach": {"Tier Rank (S-F)": "S", "Weight": 89, "Run Speed": 1.2, "Air Speed": 1.05, "Fall Speed": 1.2},
    "Daisy": {"Tier Rank (S-F)": "S", "Weight": 89, "Run Speed": 1.2, "Air Speed": 1.05, "Fall Speed": 1.2},
    "Bowser": {"Tier Rank (S-F)": "B", "Weight": 135, "Run Speed": 1.88, "Air Speed": 0.9, "Fall Speed": 1.4},
    "Ice Climbers": {"Tier Rank (S-F)": "B", "Weight": 92, "Run Speed": 1.26, "Air Speed": 1.05, "Fall Speed": 1.3},
    "Sheik": {"Tier Rank (S-F)": "B", "Weight": 78, "Run Speed": 2.05, "Air Speed": 1.07, "Fall Speed": 1.7},
    "Zelda": {"Tier Rank (S-F)": "B", "Weight": 85, "Run Speed": 1.25, "Air Speed": 1.05, "Fall Speed": 1.4},
    "Dr. Mario": {"Tier Rank (S-F)": "C", "Weight": 98, "Run Speed": 1.43, "Air Speed": 1.05, "Fall Speed": 1.2},
    "Pichu": {"Tier Rank (S-F)": "C", "Weight": 62, "Run Speed": 1.83, "Air Speed": 1.05, "Fall Speed": 1.68},
    "Falco": {"Tier Rank (S-F)": "B", "Weight": 82, "Run Speed": 1.61, "Air Speed": 1.05, "Fall Speed": 1.68},
    "Marth": {"Tier Rank (S-F)": "A", "Weight": 90, "Run Speed": 1.6, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Lucina": {"Tier Rank (S-F)": "A", "Weight": 90, "Run Speed": 1.6, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Young Link": {"Tier Rank (S-F)": "A", "Weight": 84, "Run Speed": 1.51, "Air Speed": 1.28, "Fall Speed": 1.5},
    "Ganondorf": {"Tier Rank (S-F)": "C", "Weight": 113, "Run Speed": 1.32, "Air Speed": 0.9, "Fall Speed": "Close Combat"},
    "Mewtwo": {"Tier Rank (S-F)": "B", "Weight": 79, "Run Speed": 1.8, "Air Speed": 1.35, "Fall Speed": 1.5},
    "Roy": {"Tier Rank (S-F)": "S", "Weight": 95, "Run Speed": 1.78, "Air Speed": 1.3, "Fall Speed": 1.4},
    "Chrom": {"Tier Rank (S-F)": "W", "Weight": 95, "Run Speed": 1.78, "Air Speed": 1.08, "Fall Speed": 1.4},
    "Mr. Game & Watch": {"Tier Rank (S-F)": "A", "Weight": 75, "Run Speed": 1.5, "Air Speed": 1.4, "Fall Speed": 1.8},
    "Meta Knight": {"Tier Rank (S-F)": "B", "Weight": 80, "Run Speed": 1.8, "Air Speed": 1.2, "Fall Speed": "Close Combat"},
    "Pit": {"Tier Rank (S-F)": "B", "Weight": 96, "Run Speed": 1.55, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Dark Pit": {"Tier Rank (S-F)": "B", "Weight": 96, "Run Speed": 1.55, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Zero Suit Samus": {"Tier Rank (S-F)": "S", "Weight": 80, "Run Speed": 2.0, "Air Speed": 1.05, "Fall Speed": 1.7},
    "Wario": {"Tier Rank (S-F)": "A", "Weight": 107, "Run Speed": 1.5, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Snake": {"Tier Rank (S-F)": "S", "Weight": 107, "Run Speed": 1.1, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Ike": {"Tier Rank (S-F)": "B", "Weight": 107, "Run Speed": 1.36, "Air Speed": 0.9, "Fall Speed": 1.4},
    "Pokémon Trainer": {"Tier Rank (S-F)": "S", "Weight": "N/A", "Run Speed": "Varies", "Air Speed": "Varies", "Fall Speed": "Varies"},
    "Diddy Kong": {"Tier Rank (S-F)": "A", "Weight": 90, "Run Speed": 2.1, "Air Speed": 1.1, "Fall Speed": 1.6},
    "Lucas": {"Tier Rank (S-F)": "B", "Weight": 94, "Run Speed": 1.58, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Sonic": {"Tier Rank (S-F)": "B", "Weight": 84, "Run Speed": 3.85, "Air Speed": 1.4, "Fall Speed": 1.4},
    "King Dedede": {"Tier Rank (S-F)": "B", "Weight": 127, "Run Speed": 1.32, "Air Speed": 0.88, "Fall Speed": 1.4},
    "Olimar": {"Tier Rank (S-F)": "B", "Weight": 79, "Run Speed": 1.45, "Air Speed": 1.1, "Fall Speed": 1.5},
    "Lucario": {"Tier Rank (S-F)": "B", "Weight": 90, "Run Speed": 1.7, "Air Speed": 1.2, "Fall Speed": 1.4},
    "R.O.B.": {"Tier Rank (S-F)": "S", "Weight": 106, "Run Speed": 1.5, "Air Speed": 1.05, "Fall Speed": 1.5},
    "Toon Link": {"Tier Rank (S-F)": "A", "Weight": 84, "Run Speed": 1.51, "Air Speed": 1.28, "Fall Speed": 1.28},
    "Wolf": {"Tier Rank (S-F)": "A", "Weight": 92, "Run Speed": 1.65, "Air Speed": 1.05, "Fall Speed": 1.6},
    "Villager": {"Tier Rank (S-F)": "B", "Weight": 92, "Run Speed": 1.4, "Air Speed": 1.1, "Fall Speed": 1.3},
    "Mega Man": {"Tier Rank (S-F)": "B", "Weight": 102, "Run Speed": 1.43, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Wii Fit Trainer": {"Tier Rank (S-F)": "B", "Weight": 96, "Run Speed": 1.6, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Rosalina & Lumal": {"Tier Rank (S-F)": "A", "Weight": 78, "Run Speed": 1.35, "Air Speed": 1.2, "Fall Speed": 1.3},
    "Little Mac": {"Tier Rank (S-F)": "C", "Weight": 87, "Run Speed": 2.3, "Air Speed": 0.7, "Fall Speed": 1.5},
    "Greninja": {"Tier Rank (S-F)": "A", "Weight": 82, "Run Speed": 2.05, "Air Speed": 1.75, "Fall Speed": 1.6},
    "Palutena": {"Tier Rank (S-F)": "S", "Weight": 91, "Run Speed": 1.75, "Air Speed": 1.1, "Fall Speed": 1.5},
    "Pac-Man": {"Tier Rank (S-F)": "A", "Weight": 95, "Run Speed": 1.65, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Robin": {"Tier Rank (S-F)": "B", "Weight": 94, "Run Speed": 1.3, "Air Speed": 0.95, "Fall Speed": 1.25},
    "Shulk": {"Tier Rank (S-F)": "A", "Weight": 97, "Run Speed": 1.55, "Air Speed": 1.1, "Fall Speed": "Close Combat"},
    "Bowser Jr.": {"Tier Rank (S-F)": "B", "Weight": 100, "Run Speed": 1.4, "Air Speed": 0.95, "Fall Speed": 1.3},
    "Duck Hunt": {"Tier Rank (S-F)": "B", "Weight": 86, "Run Speed": 1.4, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Ryu": {"Tier Rank (S-F)": "B", "Weight": 103, "Run Speed": 1.3, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Ken": {"Tier Rank (S-F)": "B", "Weight": 103, "Run Speed": 1.3, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Cloud": {"Tier Rank (S-F)": "S", "Weight": 100, "Run Speed": 1.7, "Air Speed": 0.95, "Fall Speed": 1.6},
    "Corrin": {"Tier Rank (S-F)": "B", "Weight": 97, "Run Speed": 1.45, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Bayonetta": {"Tier Rank (S-F)": "C", "Weight": 81, "Run Speed": 1.8, "Air Speed": 1.05, "Fall Speed": 1.6},
    "Inkling": {"Tier Rank (S-F)": "A", "Weight": 94, "Run Speed": 1.85, "Air Speed": 1.1, "Fall Speed": 1.5},
    "Ridley": {"Tier Rank (S-F)": "B", "Weight": 107, "Run Speed": 1.55, "Air Speed": 1.05, "Fall Speed": 1.6},
    "Simon": {"Tier Rank (S-F)": "B", "Weight": 107, "Run Speed": 1.1, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Richter": {"Tier Rank (S-F)": "B", "Weight": 107, "Run Speed": 1.1, "Air Speed": 0.9, "Fall Speed": 1.5},
    "King K. Rool": {"Tier Rank (S-F)": "B", "Weight": 133, "Run Speed": 1.25, "Air Speed": 0.85, "Fall Speed": 1.4},
    "Isabelle": {"Tier Rank (S-F)": "B", "Weight": 84, "Run Speed": 1.18, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Incineroar": {"Tier Rank (S-F)": "B", "Weight": 116, "Run Speed": 1.2, "Air Speed": 0.85, "Fall Speed": 1.4},
    "Piranha Plant": {"Tier Rank (S-F)": "C", "Weight": 112, "Run Speed": 1.2, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Joker": {"Tier Rank (S-F)": "S", "Weight": 93, "Run Speed": 1.95, "Air Speed": 0.95, "Fall Speed": 1.6},
    "Hero": {"Tier Rank (S-F)": "B", "Weight": 101, "Run Speed": 1.55, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Banjo & Kazooie": {"Tier Rank (S-F)": "A", "Weight": 106, "Run Speed": 1.5, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Terry Bogard": {"Tier Rank (S-F)": "A", "Weight": 108, "Run Speed": 1.6, "Air Speed": 0.9, "Fall Speed": 1.4},
    "Byleth": {"Tier Rank (S-F)": "B", "Weight": 97, "Run Speed": 1.45, "Air Speed": 0.9, "Fall Speed": 1.4},
    "Min Min": {"Tier Rank (S-F)": "S", "Weight": 104, "Run Speed": 1.55, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Steve": {"Tier Rank (S-F)": "S", "Weight": 92, "Run Speed": 1.3, "Air Speed": 0.9, "Fall Speed": 1.4},
    "Sephiroth": {"Tier Rank (S-F)": "S", "Weight": 104, "Run Speed": 1.7, "Air Speed": 0.95, "Fall Speed": 1.6},
    "Pyra/Mythra": {"Tier Rank (S-F)": "S", "Weight": 98, "Run Speed": 1.6, "Air Speed": 1.1, "Fall Speed": 1.5},
    "Kazuya": {"Tier Rank (S-F)": "S", "Weight": 109, "Run Speed": 1.5, "Air Speed": 0.9, "Fall Speed": 1.5},
    "Sora": {"Tier Rank (S-F)": "S", "Weight": 79, "Run Speed": 1.95, "Air Speed": 1.05, "Fall Speed": 1.2},
    "Mii Brawler": {"Tier Rank (S-F)": "B", "Weight": 94, "Run Speed": 1.6, "Air Speed": 1.1, "Fall Speed": 1.4},
    "Mii Swordfighter": {"Tier Rank (S-F)": "B", "Weight": 97, "Run Speed": 1.5, "Air Speed": 0.95, "Fall Speed": 1.4},
    "Mii Gunner": {"Tier Rank (S-F)": "B", "Weight": 97, "Run Speed": 1.35, "Air Speed": 0.95, "Fall Speed": 1.4}
}

# --- Custom CSS (Slightly modified from last version for clarity) ---
st.markdown("""
<style>
/* Base Styles for the Bracket Generator */
.match-box { 
    border: 1px solid #ddd; 
    border-radius: 10px; 
    padding: 6px 8px; 
    margin: 6px 0; 
    font-size: 14px; 
    line-height: 1.25; 
    background: #fff; 
}
.round-title { 
    font-weight: 700; 
    margin-bottom: 8px; 
}
.name-line { 
    display: flex; 
    align-items: center; 
    gap: 6px; 
}
.name-line img { vertical-align: middle; }
.tbd { 
    opacity: 0.6; 
    font-style: italic; 
}
.legend-badge { 
    display: inline-block; 
    width: 10px; 
    height: 10px; 
    border-radius: 2px; 
    margin-right: 6px; 
    vertical-align: middle; 
}
.small { 
    font-size: 13px; 
}

/* Custom Styles for Character Comparison Cards */
.comparison-card {
    background-color: #f7f9fb;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-top: 5px solid; /* Placeholder for color coding */
}

.char-title {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 10px;
}

.char-stat-label {
    font-weight: 600;
    margin-top: 10px;
    font-size: 14px;
}

/* Style for Round Robin Leaderboard */
.leaderboard-container {
    padding: 10px;
    border-radius: 10px;
    background-color: #f0f2f6;
    margin-top: 20px;
}
.leaderboard-title {
    font-size: 18px;
    font-weight: 700;
    color: #333;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------- Data types ----------------------------
@dataclass(frozen=True)
class Entry:
    player: str
    character: str

# ---------------------------- Power-of-two helpers ----------------------------
def next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()

def byes_needed(n: int) -> int:
    return max(0, next_power_of_two(n) - n)

# ---------------------------- Icons & colors ----------------------------
ICON_DIR = os.path.join(os.path.dirname(__file__), "images")

def get_character_icon_path(char_name: str) -> Optional[str]:
    # Placeholder for local path check (removed os.path.exists check)
    return None 

TEAM_COLOR_FALLBACKS = [
    "#E91E63", "#3F51B5", "#009688", "#FF9800", "#9C27B0",
    "#4CAF50", "#2196F3", "#FF5722", "#795548", "#607D8B"
]
PLAYER_FALLBACKS = [
    "#FF6F61", "#6B5B95", "#88B04B", "#F7CAC9", "#92A8D1",
    "#955251", "#B565A7", "#009B77", "#DD4124", "#45B8AC"
]

# Initialize persistent player colors
if "player_colors" not in st.session_state:
    st.session_state.player_colors = {}

def get_player_color(player: str, team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    """Retrieves the color for a player, prioritizing team color if in teams mode, 
       otherwise using a unique, persistent individual color."""
    
    # 1. Check for Team Color (only in Bracket Generator, Teams Mode)
    if st.session_state.get("page") == "Bracket Generator" and st.session_state.get("rule_select") == "teams":
        t = team_of.get(player, "")
        if t and team_colors.get(t):
            return team_colors[t]
    
    # 2. Use Unique Persistent Player Color (for all modes)
    if player not in st.session_state.player_colors:
        current_index = len(st.session_state.player_colors) % len(PLAYER_FALLBACKS)
        st.session_state.player_colors[player] = PLAYER_FALLBACKS[current_index]
    
    return st.session_state.player_colors[player]


def render_name_html(player: str, team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    """Renders the player name with the determined color."""
    color = get_player_color(player, team_of, team_colors)
    safe_player = player.replace("<", "&lt;").replace(">", "&gt;")
    return f"<span style='color:{color};font-weight:600'>{safe_player}</span>"

def render_entry_line(e: Optional[Entry], team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    if e is None or e.player is None or e.character is None:
        return "<div class='name-line tbd'>TBD</div>"
    if e.character.upper() == "BYE":
        return "<div class='name-line tbd'>BYE</div>"

    icon = get_character_icon_path(e.character)
    name_html = render_name_html(e.player, team_of, team_colors)
    char_safe = e.character.replace("<", "&lt;").replace(">", "&gt;")
    
    icon_html = "🎮" # Placeholder for icon
    
    if icon:
        return f"<div class='name-line'><img src='file://{icon}' width='24'/> <b>{char_safe}</b> ({name_html})</div>"
    else:
        return f"<div class='name-line'>{icon_html} <b>{char_safe}</b> ({name_html})</div>"

def entry_to_label(e: Optional[Entry]) -> str:
    if e is None: return ""
    return f"{e.player} — {e.character}"

# ---------------------------- Balanced generator (Regular core) ----------------------------
def pick_from_lowest_tally(cands: List[Entry], tally: Dict[str, int], exclude_player: Optional[str] = None) -> Optional[Entry]:
    pool = [e for e in cands if e.player != exclude_player]
    if not pool:
        return None
    m = min(tally.get(e.player, 0) for e in pool)
    lowest = [e for e in pool if tally.get(e.player, 0) == m]
    return random.choice(lowest)

def generate_bracket_balanced(
    entries: List[Entry],
    *,
    forbid_same_team: bool = False,
    team_of: Optional[Dict[str, str]] = None
) -> List[Tuple[Entry, Entry]]:
    """
    Balanced-random pairing:
      - no self-match,
      - optional: forbid same-team,
      - fills BYEs to next power of two,
      - uses per-player tallies for fairness.
    """
    team_of = team_of or {}
    base = [e for e in entries if e.player != "SYSTEM"]
    need = byes_needed(len(base))

    bag = base.copy()
    random.shuffle(bag)
    tally: Dict[str, int] = {}
    pairs: List[Tuple[Entry, Entry]] = []

    # Use some BYEs first if needed
    for _ in range(need):
        if not bag: break
        a = pick_from_lowest_tally(bag, tally)
        if not a: break
        bag.remove(a)
        pairs.append((a, Entry("SYSTEM", "BYE")))
        tally[a.player] = tally.get(a.player, 0) + 1

    def pick_opponent(a: Entry, pool: List[Entry]) -> Optional[Entry]:
        pool2 = [x for x in pool if x.player != a.player]
        if forbid_same_team:
            ta = team_of.get(a.player, "")
            if ta:
                pool2 = [x for x in pool2 if team_of.get(x.player, "") != ta]
        if not pool2:
            return None
        m = min(tally.get(x.player, 0) for x in pool2)
        lowest = [x for x in pool2 if tally.get(x.player, 0) == m]
        return random.choice(lowest)

    while len(bag) >= 2:
        a = pick_from_lowest_tally(bag, tally)
        if not a: break
        bag.remove(a)
        b = pick_opponent(a, bag)
        
        if b is None:
            if byes_needed(len(bag)+1) > 0 and bag: 
                pairs.append((a, Entry("SYSTEM", "BYE")))
                tally[a.player] = tally.get(a.player, 0) + 1
            else:
                bag.append(a)
                random.shuffle(bag)
                if len(bag) == 1:
                    break
            continue
            
        bag.remove(b)
        pairs.append((a, b))
        tally[a.player] = tally.get(a.player, 0) + 1
        tally[b.player] = tally.get(b.player, 0) + 1

    if bag: # odd leftover
        pairs.append((bag[0], Entry("SYSTEM", "BYE")))
        
    return pairs

def generate_bracket_regular(entries: List[Entry]) -> List[Tuple[Entry, Entry]]:
    return generate_bracket_balanced(entries)

def generate_bracket_teams(entries: List[Entry], team_of: Dict[str, str]) -> List[Tuple[Entry, Entry]]:
    return generate_bracket_balanced(entries, forbid_same_team=True, team_of=team_of)

# ---------------------------- Rounds building & rendering (Modified for R1 only) ----------------------------
def compute_rounds_pairs(r1_pairs: List[Tuple[Entry, Entry]], winners_map: Dict[int, str]) -> List[List[Tuple[Optional[Entry], Optional[Entry]]]]:
    # This function is retained, but the rendering will only use rounds[0]
    rounds: List[List[Tuple[Optional[Entry], Optional[Entry]]]] = []
    rounds.append([(a, b) for (a, b) in r1_pairs])

    total_real = sum(1 for (a, b) in r1_pairs for e in (a, b) if e and e.player != "SYSTEM")
    target = next_power_of_two(total_real)
    num_rounds = int(math.log2(target)) if target >= 2 else 1

    prev = rounds[0]

    def winner_of_pair(pair_index: int, pairs_list: List[Tuple[Optional[Entry], Optional[Entry]]]) -> Optional[Entry]:
        if pair_index >= len(pairs_list): return None
        a, b = pairs_list[pair_index]
        if a is None and b is None: return None
        if a is None: return b if (b and b.character.upper() != "BYE") else None
        if b is None: return a if (a and a.character.upper() != "BYE") else None
        if a.character.upper() == "BYE" and b.character.upper() != "BYE": return b
        if b.character.upper() == "BYE" and a.character.upper() != "BYE": return a

        # Only R1 has explicit selections
        label_a, label_b = entry_to_label(a), entry_to_label(b)
        sel = winners_map.get(pair_index + 1, "")
        if sel == label_a: return a
        if sel == label_b: return b
        return None

    # This loop calculates all future rounds, but only R1 winners are used/displayed
    for _ in range(1, num_rounds):
        nxt: List[Tuple[Optional[Entry], Optional[Entry]]] = []
        for i in range(0, len(prev), 2):
            w1 = winner_of_pair(i, prev)
            w2 = winner_of_pair(i + 1, prev)
            nxt.append((w1, w2))
        rounds.append(nxt)
        prev = nxt
    return rounds

def render_bracket_grid(all_rounds: List[List[Tuple[Optional[Entry], Optional[Entry]]]], team_of: Dict[str, str], team_colors: Dict[str, str]):
    # RENDER ONLY ROUND 1 (as requested)
    if not all_rounds: return

    # Ensure we only process the first round list
    round_pairs = all_rounds[0]
    
    # Team Legend
    if team_colors and any(team_of.values()) and st.session_state.get("rule_select") == "teams":
        legend = "  ".join([f"<span class='legend-badge' style='background:{c}'></span>{t}" for t, c in team_colors.items()])
        st.markdown(f"<div class='small'><b>Legend (Teams):</b> {legend}</div>", unsafe_allow_html=True)
    
    # Use st.columns(1) to make a single column display for R1
    col = st.columns(1)[0]
    
    with col:
        st.markdown("<div class='round-title'>Round 1 Pairings</div>", unsafe_allow_html=True)
        
        for pair in round_pairs:
            a, b = pair
            
            st.markdown("<div class='match-box'>", unsafe_allow_html=True)
            st.markdown(render_entry_line(a, team_of, team_colors), unsafe_allow_html=True)
            st.markdown(render_entry_line(b, team_of, team_colors), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

def r1_winner_controls(r1_pairs: List[Tuple[Entry, Entry]]):
    if "r1_winners" not in st.session_state:
        st.session_state.r1_winners = {}
    st.write("### ➡️ Select Round 1 Winners")
    
    cols = st.columns(min(3, len(r1_pairs)))
    col_idx = 0
    
    for i, (a, b) in enumerate(r1_pairs, start=1):
        # Skip BYE matches in manual selection
        if a.character.upper() == "BYE" or b.character.upper() == "BYE":
            continue
            
        with cols[col_idx % len(cols)]:
            label_a = entry_to_label(a)
            label_b = entry_to_label(b)
            prev = st.session_state.r1_winners.get(i, "")
            
            if prev == label_a: idx = 0
            elif prev == label_b: idx = 1
            else: idx = 2
            
            st.radio(
                f"Match {i}",
                options=[label_a, label_b, "(undecided)"],
                index=idx,
                key=f"winner_{i}",
                horizontal=False,
            )
            choice = st.session_state[f"winner_{i}"]
            st.session_state.r1_winners[i] = choice if choice != "(undecided)" else ""
            
        col_idx += 1

# ---------------------------- Table helpers ----------------------------
def build_entries_df(players: List[str], k: int) -> pd.DataFrame:
    rows = []
    for _ in range(k):
        for p in players:
            rows.append({"Player": p, "Character": ""})
    return pd.DataFrame(rows)

def auto_fill_characters(df: pd.DataFrame, players: List[str], k: int, shuffle_each: bool) -> pd.DataFrame:
    out = df.copy()
    for p in players:
        idxs = list(out.index[out["Player"] == p])
        labels = [random.choice(SMASH_CHARACTERS) for _ in range(len(idxs))] # Auto-fill with actual characters
        if shuffle_each:
            random.shuffle(labels)
        for row_i, label in zip(idxs, labels):
            out.at[row_i, "Character"] = label
    return out

def df_to_entries(df: pd.DataFrame, clean_rows_flag: bool) -> List[Entry]:
    entries: List[Entry] = []
    for _, row in df.iterrows():
        pl = str(row.get("Player", "")).strip()
        ch = str(row.get("Character", "")).strip()
        if clean_rows_flag and (not pl or not ch):
            continue
        if pl and ch and ch in SMASH_CHARACTERS: # Validate character is in our list
            entries.append(Entry(player=pl, character=ch))
        elif pl and ch:
             entries.append(Entry(player=pl, character=ch)) # Allow non-Smash characters for flexibility
    return entries

# ---------------------------- Character Data Retrieval ----------------------------

def get_char_data(char_name: str) -> Dict[str, str | float]:
    """Retrieves actual character stats from the SMASH_DATA dictionary."""
    data = SMASH_DATA.get(char_name, None)
    
    if data:
        # Reformat keys for display purposes
        return {
            "Tier Rank": data.get("Tier Rank (S-F)", "N/A"),
            "Weight": data.get("Weight", "N/A"),
            "Run Speed": data.get("Run Speed", "N/A"),
            "Air Speed": data.get("Air Speed", "N/A"),
            "Fall Speed": data.get("Fall Speed", "N/A"),
        }
    else:
        # Fallback for characters not found in the data source
        return {
            "Tier Rank": "Unknown",
            "Weight": "Unknown",
            "Run Speed": "Unknown",
            "Air Speed": "Unknown",
            "Fall Speed": "Unknown",
        }
        
def render_stat_meter(label: str, value, max_val: float, color: str):
    """Renders a labeled progress bar for a quantitative stat."""
    if isinstance(value, (int, float)):
        # Calculate progress relative to the maximum possible value
        progress = min(1.0, value / max_val)
        st.markdown(f'<p class="char-stat-label">{label}: <b>{value}</b></p>', unsafe_allow_html=True)
        # Manually create colored progress bar for better visual control (Streamlit doesn't support color args easily)
        st.markdown(f"""
        <div style="background-color: #e0e0e0; border-radius: 5px; height: 10px; margin-bottom: 5px;">
            <div style="background-color: {color}; height: 10px; width: {progress*100}%; border-radius: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # For non-numeric values (Tier, "Close Combat", "Varies")
        st.markdown(f'<p class="char-stat-label">{label}: <b>{value}</b></p>', unsafe_allow_html=True)


# ---------------------------- Round Robin Logic ----------------------------

def generate_round_robin_schedule(players: List[str]) -> List[Tuple[str, str]]:
    """Generates a list of all unique match-ups (Player A vs Player B)."""
    matches = []
    # If odd number of players, add a 'BYE' placeholder
    current_players = players.copy()
    if len(current_players) % 2 != 0:
        current_players = current_players + ['BYE']
    
    n = len(current_players)
    rounds = n - 1 # Total rounds to be played
    
    # Check if schedule exists in state and is valid for current players
    schedule_key = tuple(sorted(players))
    if "rr_schedule" not in st.session_state or st.session_state["rr_schedule"].get("players") != schedule_key:
        
        # Implementation of the circle method for scheduling
        matchups = []
        p = current_players.copy()
        
        for _ in range(rounds):
            half = n // 2
            for i in range(half):
                p1 = p[i]
                p2 = p[n - 1 - i]
                # Only add matches between actual players (skip BYE vs Player)
                if p1 != 'BYE' and p2 != 'BYE':
                    matchups.append((p1, p2))
                elif p1 != 'BYE':
                    # p1 gets the bye
                    pass
                elif p2 != 'BYE':
                    # p2 gets the bye
                    pass

            # Rotate all players except the first (or last, depending on implementation)
            p.insert(1, p.pop())
            
        # Store and initialize results/records
        st.session_state["rr_schedule"] = {
            "players": schedule_key,
            "matches": matchups,
        }
        st.session_state["rr_results"] = {}
        st.session_state["rr_records"] = {player: {"Wins": 0, "Losses": 0} for player in players if player != 'BYE'}
        
    return st.session_state["rr_schedule"]["matches"]

def update_round_robin_records():
    """Recalculates records based on rr_results."""
    records = {player: {"Wins": 0, "Losses": 0} for player in st.session_state["rr_records"].keys()}
    
    for match_id, winner in st.session_state.rr_results.items():
        if winner == "(Undecided)":
            continue
            
        # Match ID format: Player A|Player B
        p1, p2 = match_id.split('|')
        loser = p2 if winner == p1 else p1
        
        if winner in records:
            records[winner]["Wins"] += 1
        if loser in records:
            records[loser]["Losses"] += 1
            
    # Update session state with new records
    st.session_state.rr_records = records

def show_round_robin_page(players: List[str]):
    st.title("🗂️ Round Robin Scheduler & Leaderboard")
    st.markdown("---")
    
    if len(players) < 2:
        st.error("Please enter at least two players in the sidebar to generate a Round Robin tournament.")
        return

    # 1. Generate/Get Schedule
    schedule = generate_round_robin_schedule(players)

    # 2. Results & Match Input
    st.subheader("Match Results Input")
    st.info(f"Total Matches to Play: **{len(schedule)}**")
    
    # Recalculate records first
    update_round_robin_records()
    
    cols = st.columns(3)
    
    for i, (p1, p2) in enumerate(schedule, start=1):
        match_id = f"{p1}|{p2}"
        
        # --- FIX: RENDER MATCH TITLE WITH HTML USING MARKDOWN ---
        p1_color = get_player_color(p1, {}, {})
        p2_color = get_player_color(p2, {}, {})
        
        p1_html = f'<span style="color:{p1_color}; font-weight: bold;">{p1}</span>'
        p2_html = f'<span style="color:{p2_color}; font-weight: bold;">{p2}</span>'
        
        # Use existing winner or default to (Undecided)
        default_winner = st.session_state.rr_results.get(match_id, "(Undecided)")
        options = [p1, p2, "(Undecided)"]
        
        # Determine the default index based on the actual winner name
        try:
            default_index = options.index(default_winner)
        except ValueError:
            default_index = 2

        with cols[i % len(cols)]:
            # Render the title as HTML using st.markdown
            st.markdown(f"**Match {i}:** {p1_html} vs {p2_html}", unsafe_allow_html=True)
            
            # Use plain names for the radio options, which Streamlit handles correctly
            winner = st.radio(
                f"Winner (Match {i})",
                options=options,
                index=default_index,
                key=f"rr_winner_{match_id}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # Update results if a choice was made
            st.session_state.rr_results[match_id] = winner
            
    # 3. Leaderboard Display
    st.markdown("---")
    st.subheader("🏆 Tournament Leaderboard")
    
    # Sort the records: by Wins (descending), then Losses (ascending)
    records_df = pd.DataFrame.from_dict(st.session_state.rr_records, orient='index')
    
    if not records_df.empty:
        # Add color column for display
        records_df.reset_index(names=['Player'], inplace=True)
        
        records_df["Win Rate"] = records_df.apply(lambda row: row['Wins'] / (row['Wins'] + row['Losses']) if (row['Wins'] + row['Losses']) > 0 else 0, axis=1)
        records_df.sort_values(by=['Wins', 'Losses', 'Player'], ascending=[False, True, True], inplace=True)
        records_df.index = records_df.index + 1 # Start index at 1
        
        st.dataframe(
            records_df, 
            use_container_width=True,
            column_config={
                "Player": st.column_config.Column("Player", width="small"),
                "Wins": st.column_config.Column("Wins", width="small"),
                "Losses": st.column_config.Column("Losses", width="small"),
                "Win Rate": st.column_config.ProgressColumn("Win Rate", format="%.1f", width="small", min_value=0, max_value=1),
            }
        )
    else:
        st.info("No records to display. Please enter match results.")
        
    st.markdown("---")
    if st.button("🔄 Reset All Round Robin Records"):
        st.session_state["rr_results"] = {}
        st.session_state["rr_records"] = {player: {"Wins": 0, "Losses": 0} for player in players if player != 'BYE'}
        st.session_state.pop("rr_schedule", None)
        st.rerun()

# ---------------------------- App Pages ----------------------------
def show_bracket_generator_page(players, team_of, team_colors, clean_rows):
    st.title("🎮 Smash Bracket — Round 1 Generator")

    # ---------------------------- State & editor ----------------------------
    if "table_df" not in st.session_state:
        st.session_state.table_df = pd.DataFrame([
            {"Player": "You", "Character": "Mario"},
            {"Player": "You", "Character": "Link"},
            {"Player": "Friend1", "Character": "Kirby"},
            {"Player": "Friend1", "Character": "Fox"},
            {"Player": "Friend2", "Character": "Samus"},
        ])

    if st.session_state.get("build_clicked"):
        if not players:
            st.warning("Add at least one player in the sidebar before building entries.")
        else:
            st.session_state.table_df = build_entries_df(players, int(st.session_state.chars_per_person))
            st.session_state.pop("last_bracket", None)
            st.session_state.pop("r1_winners", None)
            st.session_state.pop("build_clicked") # Clear click state
            st.rerun()

    if st.session_state.get("auto_fill_clicked"):
        if not players:
            st.warning("Add players first.")
        else:
            st.session_state.table_df = auto_fill_characters(
                st.session_state.table_df, players, int(st.session_state.chars_per_person), st.session_state.shuffle_within_player
            )
            st.session_state.pop("auto_fill_clicked")
            st.rerun()

    if players:
        st.session_state.table_df["Player"] = st.session_state.table_df["Player"].apply(
            lambda p: p if p in players else (players[0] if players and p == "" else p)
        )

    st.subheader("Entries")
    table_df = st.data_editor(
        st.session_state.table_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Player": st.column_config.SelectboxColumn("Player", options=players if players else [], required=True),
            "Character": st.column_config.SelectboxColumn("Character", options=SMASH_CHARACTERS, required=True),
        },
        key="table_editor",
    )
    entries = df_to_entries(table_df, clean_rows_flag=clean_rows)

    # ---------------------------- Generate & show ----------------------------
    st.divider()
    col_gen, col_clear = st.columns([2, 1])

    with col_gen:
        if st.button("🎲 Generate Round 1 Bracket", type="primary"):
            if len(entries) < 2:
                st.error("Add at least 2 entries (characters).")
            else:
                rule = st.session_state.rule # Use rule from sidebar
                if rule == "regular":
                    bracket = generate_bracket_regular(entries)
                else:  # teams
                    bracket = generate_bracket_teams(entries, team_of)

                if not bracket:
                    st.error("Couldn't build a valid round-1 bracket with those constraints.")
                else:
                    total_real = len([e for e in entries if e.player != "SYSTEM"])
                    target = next_power_of_two(total_real)
                    need = target - total_real
                    st.success(f"Entries: {total_real} → Target: {target} (BYEs: {need}) — Mode: {rule.upper()}")

                    st.session_state["last_bracket"] = [(a, b) for (a, b) in bracket]
                    st.session_state["last_rule"] = rule
                    st.session_state["last_team_of"] = team_of if rule == "teams" else {}
                    st.session_state["last_team_colors"] = team_colors if rule == "teams" else {}
                    st.session_state.pop("r1_winners", None) # Clear winners on new generation

    # Persist & render compact full bracket
    if "last_bracket" in st.session_state and st.session_state["last_bracket"]:
        r1_pairs = st.session_state["last_bracket"]
        if st.session_state.get("last_rule") == "teams":
            st.info("Bracket view — Teams mode")
        else:
            st.info("Bracket view — Regular mode")

        st.subheader("Round 1 Pairings")
        r1_winner_controls(r1_pairs) # Display winner controls for R1
        
        rounds = compute_rounds_pairs(r1_pairs, st.session_state.get("r1_winners", {}))
        # Only render the first round
        render_bracket_grid(rounds[:1], st.session_state.get("last_team_of", {}), st.session_state.get("last_team_colors", {}))

    with col_clear:
        if st.button("🧹 Clear Table"):
            st.session_state.table_df = pd.DataFrame(columns=["Player", "Character"])
            st.session_state.pop("last_bracket", None)
            st.session_state.pop("r1_winners", None)
            st.rerun()

    st.caption("Round 1 generation uses balanced randomization; Teams forbids same-team R1. Character icons are placeholders.")


def show_character_info_page():
    st.title("📚 Smash Bros. Character Info & Comparison")
    st.markdown("---")
    
    # Use two separate selectboxes for comparison
    col_select1, col_select2 = st.columns(2)

    with col_select1:
        char_selection1 = st.selectbox(
            "Character 1", 
            options=SMASH_CHARACTERS, 
            key="char_select_1",
            index=SMASH_CHARACTERS.index("Mario") if "Mario" in SMASH_CHARACTERS else 0
        )
    
    with col_select2:
        # Filter options to prevent selecting the same character in both slots
        filtered_options = [c for c in SMASH_CHARACTERS if c != char_selection1]
        
        # Determine the default index for Character 2
        default_index = 0
        if "Link" in filtered_options:
            default_index = filtered_options.index("Link")
        elif len(filtered_options) > 0:
            default_index = 0
            
        char_selection2 = st.selectbox(
            "Character 2", 
            options=filtered_options, 
            key="char_select_2",
            index=default_index
        )
    
    st.divider()

    # Create the list of selected characters (guaranteed to be 2)
    char_selections = [char_selection1, char_selection2]
    
    # --- Maximum values for visual comparison bars (based on provided data) ---
    MAX_WEIGHT = 135 # Bowser
    MAX_RUN_SPEED = 3.85 # Sonic
    MAX_AIR_SPEED = 1.75 # Greninja
    MAX_FALL_SPEED = 1.8 # Fox

    # Create two columns for the character cards
    col1, col2 = st.columns(2)
    
    # --- RENDER CHARACTER 1 ---
    char1_data = get_char_data(char_selection1)
    with col1:
        st.markdown(f'<div class="comparison-card" style="border-top-color: #3F51B5;">', unsafe_allow_html=True)
        st.markdown(f'<p class="char-title">{char_selection1}</p>', unsafe_allow_html=True)
        # Placeholder for image
        st.image(f"https://placehold.co/100x100/3F51B5/ffffff?text={char_selection1[0]}", width=100, caption="Character Image")

        st.markdown("---")
        
        # Tier Rank (Fixed value)
        st.markdown(f'<p class="char-stat-label">Tier Rank: <b>{char1_data["Tier Rank"]}</b></p>', unsafe_allow_html=True)
        
        # Weight comparison
        render_stat_meter("Weight", char1_data["Weight"], MAX_WEIGHT, "#4CAF50")
        
        # Run Speed comparison
        render_stat_meter("Run Speed", char1_data["Run Speed"], MAX_RUN_SPEED, "#FF9800")
        
        # Air Speed comparison
        render_stat_meter("Air Speed", char1_data["Air Speed"], MAX_AIR_SPEED, "#009688")
        
        # Fall Speed (Meter only for numeric, text for non-numeric)
        if isinstance(char1_data["Fall Speed"], (int, float)):
             render_stat_meter("Fall Speed", char1_data["Fall Speed"], MAX_FALL_SPEED, "#E91E63")
        else:
             st.markdown(f'<p class="char-stat-label">Fall Speed: <b>{char1_data["Fall Speed"]}</b></p>', unsafe_allow_html=True)
             
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- RENDER CHARACTER 2 ---
    char2_data = get_char_data(char_selection2)
    with col2:
        st.markdown(f'<div class="comparison-card" style="border-top-color: #E91E63;">', unsafe_allow_html=True)
        st.markdown(f'<p class="char-title">{char_selection2}</p>', unsafe_allow_html=True)
        # Placeholder for image
        st.image(f"https://placehold.co/100x100/E91E63/ffffff?text={char_selection2[0]}", width=100, caption="Character Image")

        st.markdown("---")
        
        # Tier Rank (Fixed value)
        st.markdown(f'<p class="char-stat-label">Tier Rank: <b>{char2_data["Tier Rank"]}</b></p>', unsafe_allow_html=True)
        
        # Weight comparison
        render_stat_meter("Weight", char2_data["Weight"], MAX_WEIGHT, "#4CAF50")
        
        # Run Speed comparison
        render_stat_meter("Run Speed", char2_data["Run Speed"], MAX_RUN_SPEED, "#FF9800")
        
        # Air Speed comparison
        render_stat_meter("Air Speed", char2_data["Air Speed"], MAX_AIR_SPEED, "#009688")
        
        # Fall Speed (Meter only for numeric, text for non-numeric)
        if isinstance(char2_data["Fall Speed"], (int, float)):
             render_stat_meter("Fall Speed", char2_data["Fall Speed"], MAX_FALL_SPEED, "#E91E63")
        else:
             st.markdown(f'<p class="char-stat-label">Fall Speed: <b>{char2_data["Fall Speed"]}</b></p>', unsafe_allow_html=True)
             
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.divider()
    st.info("The comparison uses actual data from your provided file. The colored bars compare the stat value against the highest value found in the entire roster (e.g., Bowser for Weight).")

# ---------------------------- Sidebar & Main App Flow ----------------------------
# Initialize a placeholder for the page selected in the sidebar
if "page" not in st.session_state:
    st.session_state.page = "Bracket Generator"

with st.sidebar:
    st.header("App Navigation")
    # This radio button controls which main function runs
    st.session_state.page = st.radio("Switch View", options=["Bracket Generator", "Round Robin", "Character Info"], index=0)
    
    st.divider()

    # The rest of the sidebar is only for the Bracket Generator and Round Robin pages
    if st.session_state.page == "Bracket Generator" or st.session_state.page == "Round Robin":
        st.header("Players")
        default_players = "You\nFriend1\nFriend2"
        st.text_area(
            "Enter player names (one per line)",
            value=st.session_state.get("players_multiline", default_players),
            height=140,
            key="players_multiline",
            help="These names define the participants for both Bracket and Round Robin."
        )
        players = [p.strip() for p in st.session_state.players_multiline.splitlines() if p.strip()]

        if st.session_state.page == "Bracket Generator":
            st.header("Rule Set")
            st.session_state.rule = st.selectbox(
                "Choose mode",
                options=["regular", "teams"],
                index=0,
                key="rule_select",
                help="Regular: balanced random (no self-matches). Teams: regular + forbids same-team matches in Round 1."
            )
            # Bracket specific UI
            team_of: Dict[str, str] = {}
            team_colors: Dict[str, str] = {}
            if st.session_state.rule == "teams":
                st.divider()
                st.header("Teams & Colors")
                team_names_input = st.text_input(
                    "Team labels (comma separated)",
                    value="Red, Blue",
                    key="team_names_input_key",
                    help="Example: Red, Blue, Green"
                )
                team_labels = [t.strip() for t in team_names_input.split(",") if t.strip()]
                if not team_labels:
                    team_labels = ["Team A", "Team B"]

                st.caption("Pick a color for each team:")
                for i, t in enumerate(team_labels):
                    default = TEAM_COLOR_FALLBACKS[i % len(TEAM_COLOR_FALLBACKS)]
                    team_colors[t] = st.color_picker(f"{t} color", value=default, key=f"team_color_{t}")

                st.caption("Assign each player to a team:")
                for p in players:
                    team_of[p] = st.selectbox(f"{p}", options=["(none)"] + team_labels, key=f"team_{p}")
                team_of = {p: (t if t != "(none)" else "") for p, t in team_of.items()}

            st.divider()
            st.header("Characters per player")
            st.number_input("How many per player?", min_value=1, max_value=50, value=2, step=1, key="chars_per_person")

            st.divider()
            st.subheader("Build / Fill")
            st.button("⚙️ Auto-Create/Reset Entries", use_container_width=True, key="build_clicked")
            st.checkbox("Shuffle names when auto-filling", value=True, key="shuffle_within_player")
            st.button("🎲 Auto-fill Characters", use_container_width=True, key="auto_fill_clicked")

            st.divider()
            st.header("General")
            clean_rows = st.checkbox("Remove empty rows", value=True)
            
        else: # Round Robin page needs these defined
             team_of, team_colors, clean_rows = {}, {}, True # Not used in RR, but defined

    else: # Character Info page needs these defined
        players, team_of, team_colors, clean_rows = [], {}, {}, True


# --- Main Content Render ---
if st.session_state.page == "Bracket Generator":
    # Ensure all required variables are set before calling the function
    try:
        rule = st.session_state.rule
    except AttributeError:
        # Default settings if coming from another page
        rule = "regular"
        players = [p.strip() for p in st.session_state.get("players_multiline", "You\nFriend1\nFriend2").splitlines() if p.strip()]
        team_of = {}
        team_colors = {}
        clean_rows = True
        
    show_bracket_generator_page(players, team_of, team_colors, clean_rows)
elif st.session_state.page == "Round Robin":
    # Get player list from sidebar state
    players = [p.strip() for p in st.session_state.get("players_multiline", "You\nFriend1\nFriend2").splitlines() if p.strip()]
    show_round_robin_page(players)
else:
    show_character_info_page()
