import streamlit as st
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import pandas as pd
import math
import os

st.set_page_config(page_title="Smash Bracket", page_icon="🎮", layout="wide")
st.markdown("""
<style>
/* Improved styling for clarity and modern look */
.match-box { aimport streamlit as st
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
import pandas as pd
import math
import os

st.set_page_config(page_title="Smash Bracket", page_icon="🎮", layout="wide")

# --- Smash Ultimate Character List (for use in data entry and info page) ---
SMASH_CHARACTERS = [
    "Mario", "Donkey Kong", "Link", "Samus", "Yoshi", "Kirby", "Fox", "Pikachu", 
    "Luigi", "Captain Falcon", "Jigglypuff", "Peach", "Daisy", "Bowser", "Ice Climbers",
    "Sheik", "Zelda", "Dr. Mario", "Pichu", "Falco", "Marth", "Lucina", "Young Link", 
    "Ganondorf", "Mewtwo", "Roy", "Chrom", "Mr. Game & Watch", "Meta Knight", 
    "Pit", "Dark Pit", "Zero Suit Samus", "Wario", "Snake", "Ike", "Pokémon Trainer", 
    "Diddy Kong", "Lucas", "Sonic", "King Dedede", "Olimar", "Lucario", "R.O.B.", 
    "Toon Link", "Wolf", "Villager", "Mega Man", "Wii Fit Trainer", "Rosalina & Luma", 
    "Little Mac", "Greninja", "Palutena", "Pac-Man", "Robin", "Shulk", "Bowser Jr.", 
    "Duck Hunt", "Ryu", "Ken", "Cloud", "Corrin", "Bayonetta", "Inkling", "Ridley", 
    "Simon", "Richter", "King K. Rool", "Isabelle", "Incineroar", "Piranha Plant", 
    "Joker", "Hero", "Banjo & Kazooie", "Terry", "Byleth", "Min Min", "Steve", 
    "Sephiroth", "Pyra", "Mythra", "Kazuya", "Sora", "Mii Brawler", "Mii Swordfighter", 
    "Mii Gunner"
]

# --- Custom CSS (Slightly modified from last version for clarity) ---
st.markdown("""
<style>
.match-box { 
    border:1px solid #ddd; 
    border-radius:10px; 
    padding:6px 8px; 
    margin:6px 0;
    font-size:14px; 
    line-height:1.25; 
    background:#fff; 
}
.round-title { 
    font-weight:700; 
    margin-bottom:8px; 
}
.name-line { 
    display:flex; 
    align-items:center; 
    gap:6px; 
}
.name-line img { vertical-align:middle; }
.tbd { 
    opacity:0.6; 
    font-style:italic; 
}
.legend-badge { 
    display:inline-block; 
    width:10px; 
    height:10px; 
    border-radius:2px; 
    margin-right:6px; 
    vertical-align:middle; 
}
.small { 
    font-size:13px; 
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

def render_name_html(player: str, team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    t = team_of.get(player, "")
    if t and team_colors.get(t):
        color = team_colors[t]
    else:
        # Use session state for persistent player color
        if player not in st.session_state.player_colors:
            current_index = len(st.session_state.player_colors) % len(PLAYER_FALLBACKS)
            st.session_state.player_colors[player] = PLAYER_FALLBACKS[current_index]
        color = st.session_state.player_colors[player]
        
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
    if team_colors and any(team_of.values()):
        legend = "  ".join([f"<span class='legend-badge' style='background:{c}'></span>{t}" for t, c in team_colors.items()])
        st.markdown(f"<div class='small'><b>Legend:</b> {legend}</div>", unsafe_allow_html=True)
    
    # Use st.columns(1) to make a single column display for R1
    col = st.columns(1)[0]
    
    with col:
        st.markdown("<div class='round-title'>Round 1 Pairings</div>", unsafe_allow_html=True)
        
        for pair in round_pairs:
            a, b = pair
            # Use persistent player_colors from session state
            player_colors = st.session_state.player_colors
            
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
    st.title("📚 Smash Bros. Character Info")
    st.markdown("---")
    
    st.subheader("Select a Character for Mock Details")
    
    char_selection = st.selectbox("Character", options=SMASH_CHARACTERS)
    
    st.divider()
    
    # Generate Mock Data for the selected character
    # Ensures the mock data is consistent once selected by hashing the character name
    random.seed(char_selection) 
    
    mock_stats = {
        "Weight Class": random.choice(["Light", "Medium", "Heavy", "Super-Heavy"]),
        "Tier Rank (Approx.)": random.choice(["S", "A+", "A", "B+", "B", "C"]),
        "Dash Speed": f"{random.uniform(1.0, 3.0):.2f}",
        "Fall Speed": f"{random.uniform(1.0, 2.0):.2f}",
        "Recommended Playstyle": random.choice(["Aggressive Rushdown", "Zoning/Defensive", "Bait & Punish", "Grappler"]),
    }
    random.seed(None) # Reset seed

    st.subheader(f"Stats: {char_selection}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Weight Class", mock_stats["Weight Class"])
        st.metric("Dash Speed", mock_stats["Dash Speed"])

    with col2:
        st.metric("Tier Rank", mock_stats["Tier Rank (Approx.)"])
        st.metric("Fall Speed", mock_stats["Fall Speed"])
        
    with col3:
        st.metric("Playstyle", mock_stats["Recommended Playstyle"])
        
    st.divider()
    st.info(f"**About {char_selection}:** This data is generated for illustrative purposes only. For competitive play, always consult official frame data and tournament resources.")

# ---------------------------- Sidebar & Main App Flow ----------------------------
# Initialize a placeholder for the page selected in the sidebar
if "page" not in st.session_state:
    st.session_state.page = "Bracket Generator"

with st.sidebar:
    st.header("App Navigation")
    # This radio button controls which main function runs
    st.session_state.page = st.radio("Switch View", options=["Bracket Generator", "Character Info"], index=0)
    
    st.divider()

    # The rest of the sidebar is only for the Bracket Generator page
    if st.session_state.page == "Bracket Generator":
        st.header("Rule Set")
        st.session_state.rule = st.selectbox(
            "Choose mode",
            options=["regular", "teams"],
            index=0,
            key="rule_select",
            help="Regular: balanced random (no self-matches). Teams: regular + forbids same-team matches in Round 1."
        )

        st.divider()
        st.header("Players")
        default_players = "You\nFriend1\nFriend2"
        st.text_area(
            "Enter player names (one per line)",
            value=st.session_state.get("players_multiline", default_players),
            height=140,
            key="players_multiline",
            help="These names populate the Player dropdown."
        )
        players = [p.strip() for p in st.session_state.players_multiline.splitlines() if p.strip()]

        # Teams UI only in Teams mode
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
    else:
        # Placeholder assignment when not on bracket page
        players, team_of, team_colors, clean_rows = [], {}, {}, True


# --- Main Content Render ---
if st.session_state.page == "Bracket Generator":
    show_bracket_generator_page(players, team_of, team_colors, clean_rows)
else:
    show_character_info_page()

    border: 1px solid #333; 
    border-radius: 8px; 
    padding: 8px; 
    margin: 6px 0;
    font-size: 14px; 
    line-height: 1.3; 
    background: #f8f8f8; 
    box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1); 
}
.round-title { 
    font-weight: 800; 
    margin-bottom: 8px; 
    font-size: 1.1em;
    color: #007bff; /* Blue title */
}
.name-line { 
    display: flex; 
    align-items: center; 
    gap: 6px; 
    padding: 2px 0;
}
.tbd { 
    opacity: 0.6; 
    font-style: italic; 
    color: #666;
}
.legend-badge { 
    display: inline-block; 
    width: 12px; 
    height: 12px; 
    border-radius: 50%; 
    margin-right: 6px; 
    vertical-align: middle; 
}
.champion {
    font-size: 1.5em;
    font-weight: bold;
    color: #FFD700;
    padding: 10px;
    background: #2a2a2a;
    border-radius: 8px;
    text-align: center;
}
.stRadio > label { 
    padding: 0 5px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🎮 Smash Bracket — Regular & Teams")

# ---------------------------- Data types ----------------------------
@dataclass(frozen=True)
class Entry:
    player: str
    character: str

# ---------------------------- Power-of-two helpers ----------------------------
def next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    # Handle edge case where n is already a power of two
    if (n & (n - 1) == 0):
        return n
    return 1 << n.bit_length()

def byes_needed(n: int) -> int:
    return max(0, next_power_of_two(n) - n)

# ---------------------------- Icons & colors ----------------------------
ICON_DIR = os.path.join(os.path.dirname(__file__), "images")

def get_character_icon_path(char_name: str) -> Optional[str]:
    # Keeping this function for structure, but image file access is tricky in Streamlit cloud
    if not char_name:
        return None
    fname = f"{char_name.title().replace(' ', '_')}.png"
    path = os.path.join(ICON_DIR, fname)
    return path if os.path.exists(path) else None

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

def render_name_html(player: str, team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    t = team_of.get(player, "")
    if t and team_colors.get(t):
        color = team_colors[t]
    else:
        # Use session state for persistent player color
        if player not in st.session_state.player_colors:
            current_index = len(st.session_state.player_colors) % len(PLAYER_FALLBACKS)
            st.session_state.player_colors[player] = PLAYER_FALLBACKS[current_index]
        color = st.session_state.player_colors[player]
        
    safe_player = player.replace("<", "&lt;").replace(">", "&gt;")
    return f"<span style='color:{color};font-weight:600'>{safe_player}</span>"

def render_entry_line(e: Optional[Entry], team_of: Dict[str, str], team_colors: Dict[str, str]) -> str:
    if e is None or e.player is None or e.character is None:
        return "<div class='name-line tbd'>TBD</div>"
    if e.character.upper() == "BYE":
        return "<div class='name-line tbd'>BYE (Auto-Advance)</div>"
    if e.character.upper() == "TBD":
         # Use TBD for unresolved matches in later rounds
        return "<div class='name-line tbd'>Match Winner (TBD)</div>"
        
    icon = get_character_icon_path(e.character) # Placeholder for image loading
    name_html = render_name_html(e.player, team_of, team_colors)
    char_safe = e.character.replace("<", "&lt;").replace(">", "&gt;")
    
    # Use controller emoji as fallback icon
    icon_html = "🎮" 
    
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
            # If constrained, try to add a BYE if possible (though most BYEs should be placed above)
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

# ---------------------------- Rounds building & rendering ----------------------------

# Helper to determine the winner of ANY match (R1 by user input, R2+ by logic)
def resolve_match_winner(match_index: int, pair: Tuple[Optional[Entry], Optional[Entry]], winners_map: Dict[int, str], is_r1: bool) -> Optional[Entry]:
    a, b = pair
    
    # 1. Handle BYEs (Auto-Win)
    if a and a.character.upper() == "BYE": return b if (b and b.character.upper() != "BYE") else None
    if b and b.character.upper() == "BYE": return a if (a and a.character.upper() != "BYE") else None

    # 2. Handle R1 User Selection
    if is_r1 and a and b:
        label_a, label_b = entry_to_label(a), entry_to_label(b)
        sel = winners_map.get(match_index, "")
        if sel == label_a: return a
        if sel == label_b: return b
        return None # R1 undecided

    # 3. Handle R2+ Unresolved Matches
    if not is_r1 and a and b:
        # If both opponents are real players, the match is unresolved for R2+ (since we only control R1)
        return Entry("SYSTEM", "TBD")

    # 4. Handle other unresolved cases
    return None

def compute_rounds_pairs(r1_pairs: List[Tuple[Entry, Entry]], winners_map: Dict[int, str]) -> List[List[Tuple[Optional[Entry], Optional[Entry]]]]:
    rounds: List[List[Tuple[Optional[Entry], Optional[Entry]]]] = []
    
    # --- 1. Compute R1 (using user selections) ---
    r1_matches: List[Tuple[Optional[Entry], Optional[Entry]]] = []
    resolved_r1_winners: List[Optional[Entry]] = []
    
    for i, pair in enumerate(r1_pairs):
        r1_matches.append(pair)
        # Match index starts from 1 for user map
        winner = resolve_match_winner(i + 1, pair, winners_map, is_r1=True) 
        resolved_r1_winners.append(winner)
        
    rounds.append(r1_matches)

    # Determine total rounds needed
    total_real = sum(1 for e in resolved_r1_winners if e is not None and e.character.upper() != "BYE")
    target = next_power_of_two(total_real)
    num_rounds = int(math.log2(target)) if target >= 2 else 1

    prev_winners = resolved_r1_winners
    
    # --- 2. Compute R2 and up ---
    for round_idx in range(1, num_rounds):
        current_pairs: List[Tuple[Optional[Entry], Optional[Entry]]] = []
        next_winners: List[Optional[Entry]] = []

        # Iterate through the winners of the previous round, taking two at a time
        for i in range(0, len(prev_winners), 2):
            w1 = prev_winners[i]
            w2 = prev_winners[i + 1] if i + 1 < len(prev_winners) else None

            # Create the match-up for the current round
            current_pairs.append((w1, w2))
            
            # Determine the winner of this R2+ match (must be a BYE or TBD)
            winner = None
            if w1 is None and w2 is None:
                winner = None
            elif w1 and w1.character.upper() == "BYE":
                winner = w2 if w2 and w2.character.upper() != "BYE" else Entry("SYSTEM", "TBD")
            elif w2 and w2.character.upper() == "BYE":
                winner = w1 if w1 and w1.character.upper() != "BYE" else Entry("SYSTEM", "TBD")
            elif w1 is not None and w2 is not None and w1.character.upper() != "TBD" and w2.character.upper() != "TBD":
                # If both competitors advanced, the match is unresolved for R2+
                winner = Entry("SYSTEM", "TBD")
            elif w1 is not None:
                winner = w1
            elif w2 is not None:
                winner = w2

            next_winners.append(winner)
            
        rounds.append(current_pairs)
        prev_winners = next_winners
        
    return rounds

def render_bracket_grid(all_rounds: List[List[Tuple[Optional[Entry], Optional[Entry]]]], team_of: Dict[str, str], team_colors: Dict[str, str]):
    cols = st.columns(len(all_rounds))
    
    # Team Legend
    if team_colors and any(team_of.values()):
        legend = " ".join([
            f"<span class='legend-badge' style='background:{c}'></span>{t}" 
            for t, c in team_colors.items() if t in team_of.values()
        ])
        st.markdown(f"<div class='small'><b>Legend:</b> {legend}</div>", unsafe_allow_html=True)

    for round_idx, round_pairs in enumerate(all_rounds):
        with cols[round_idx]:
            round_name = "Finals" if round_idx == len(all_rounds) - 1 else f"Round {round_idx+1}"
            st.markdown(f"<div class='round-title'>{round_name}</div>", unsafe_allow_html=True)
            
            for pair in round_pairs:
                a, b = pair
                
                # Use st.session_state.player_colors
                player_colors = st.session_state.player_colors 

                st.markdown("<div class='match-box'>", unsafe_allow_html=True)
                st.markdown(render_entry_line(a, team_of, team_colors), unsafe_allow_html=True)
                st.markdown(render_entry_line(b, team_of, team_colors), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
    # Display Champion if determined
    if all_rounds and all_rounds[-1]:
        champion_pair = all_rounds[-1][0]
        # The winner is the non-TBD/non-BYE entry in the final pair
        champion = champion_pair[0] if champion_pair[0] and champion_pair[0].character.upper() not in ["BYE", "TBD"] else champion_pair[1]
        
        if champion and champion.character.upper() not in ["BYE", "TBD"]:
            st.balloons()
            st.markdown("<div class='champion'>🏆 CHAMPION 🏆</div>", unsafe_allow_html=True)
            st.markdown(render_entry_line(champion, team_of, team_colors), unsafe_allow_html=True)

def r1_winner_controls(r1_pairs: List[Tuple[Entry, Entry]]):
    if "r1_winners" not in st.session_state:
        st.session_state.r1_winners = {}
    
    st.write("### ➡️ Select Round 1 Winners to Advance Bracket")
    
    real_matches = [(a, b) for a, b in r1_pairs if a.character.upper() not in ["BYE"] and b.character.upper() not in ["BYE"]]
    if not real_matches:
        st.info("No real matches in Round 1 (likely all BYEs). The bracket will advance automatically.")
        return

    for i, (a, b) in enumerate(r1_pairs, start=1):
        if a.character.upper() == "BYE" or b.character.upper() == "BYE":
            continue # Skip BYE matches in manual selection
            
        label_a = entry_to_label(a)
        label_b = entry_to_label(b)
        
        prev = st.session_state.r1_winners.get(i, "")
        if prev == label_a: idx = 0
        elif prev == label_b: idx = 1
        else: idx = 2
        
        # Use a label for context when radio buttons are horizontal
        st.markdown(f"**Match {i}:** {label_a} vs {label_b}")
        
        st.radio(
            f"Match {i} Winner",
            options=[label_a, label_b, "(Undecided)"],
            index=idx,
            key=f"winner_{i}",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        choice = st.session_state[f"winner_{i}"]
        st.session_state.r1_winners[i] = choice if choice != "(Undecided)" else ""

# ---------------------------- Table helpers and State/Editor (Unchanged) ----------------------------
# [Table helper functions and State/Editor blocks are here]

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
        labels = [f"Character {i+1}" for i in range(len(idxs))]
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
        if pl and ch:
            entries.append(Entry(player=pl, character=ch))
    return entries
# ---------------------------- Sidebar ----------------------------
with st.sidebar:
    st.header("Rule Set")
    rule = st.selectbox(
        "Choose mode",
        options=["regular", "teams"],
        index=0,
        help=(
            "regular: balanced random (no self-matches), fills BYEs to next power of 2.\n"
            "teams: regular + forbids same-team matches in round 1 (names colored by team)."
        )
    )

    st.divider()
    st.header("Players")
    default_players = "You\nFriend1\nFriend2"
    players_multiline = st.text_area(
        "Enter player names (one per line)",
        value=st.session_state.get("players_multiline", default_players),
        height=140,
        help="These names populate the Player dropdown."
    )
    players = [p.strip() for p in players_multiline.splitlines() if p.strip()]
    st.session_state["players_multiline"] = players_multiline

    # Teams UI only in Teams mode
    team_of: Dict[str, str] = {}
    team_colors: Dict[str, str] = {}
    if rule == "teams":
        st.divider()
        st.header("Teams & Colors")
        team_names_input = st.text_input(
            "Team labels (comma separated)",
            value="Red, Blue",
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
    chars_per_person = st.number_input("How many per player?", min_value=1, max_value=50, value=2, step=1)

    st.divider()
    st.subheader("Build / Fill")
    build_clicked = st.button("⚙️ Auto-Create/Reset Entries", use_container_width=True)
    shuffle_within_player = st.checkbox("Shuffle names when auto-filling", value=True)
    auto_fill_clicked = st.button("🎲 Auto-fill Characters (Character 1..k)", use_container_width=True)

    st.divider()
    st.header("General")
    clean_rows = st.checkbox("Remove empty rows", value=True)

# ---------------------------- State & editor ----------------------------
if "table_df" not in st.session_state:
    st.session_state.table_df = pd.DataFrame([
        {"Player": "You", "Character": "Mario"},
        {"Player": "You", "Character": "Link"},
        {"Player": "Friend1", "Character": "Kirby"},
        {"Player": "Friend1", "Character": "Fox"},
        {"Player": "Friend2", "Character": "Samus"},
    ])

if build_clicked:
    if not players:
        st.warning("Add at least one player in the sidebar before building entries.")
    else:
        st.session_state.table_df = build_entries_df(players, int(chars_per_person))

if auto_fill_clicked:
    if not players:
        st.warning("Add players first.")
    else:
        st.session_state.table_df = auto_fill_characters(
            st.session_state.table_df, players, int(chars_per_person), shuffle_within_player
        )

if players:
    st.session_state.table_df["Player"] = st.session_state.table_df["Player"].apply(
        lambda p: p if p in players else (players[0] if p == "" else p)
    )

st.subheader("Entries")
table_df = st.data_editor(
    st.session_state.table_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Player": st.column_config.SelectboxColumn("Player", options=players if players else [], required=True),
        "Character": st.column_config.TextColumn(required=True),
    },
    key="table_editor",
)
entries = df_to_entries(table_df, clean_rows_flag=clean_rows)

# ---------------------------- Generate & show ----------------------------
st.divider()
col_gen, col_clear = st.columns([2, 1])

with col_gen:
    if st.button("🎲 Generate Bracket", type="primary"):
        if len(entries) < 2:
            st.error("Add at least 2 entries (characters).")
        else:
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
                st.success(f"Entries: {total_real} → Target: {target} (BYEs: {need}) — Mode: {rule}")

                st.session_state["last_bracket"] = [(a, b) for (a, b) in bracket]
                st.session_state["last_rule"] = rule
                st.session_state["last_team_of"] = team_of if rule == "teams" else {}
                st.session_state["last_team_colors"] = team_colors if rule == "teams" else {}
                st.session_state.pop("r1_winners", None) # Clear winners on new generation

# Persist & render compact full bracket
if "last_bracket" in st.session_state and st.session_state["last_bracket"]:
    r1_pairs = st.session_state["last_bracket"]
    if st.session_state.get("last_rule") == "teams":
        st.info("Bracket view (all rounds) — Teams mode")
    else:
        st.info("Bracket view (all rounds) — Regular mode")

    r1_winner_controls(r1_pairs)
    rounds = compute_rounds_pairs(r1_pairs, st.session_state.get("r1_winners", {}))
    render_bracket_grid(
        rounds, 
        st.session_state.get("last_team_of", {}), 
        st.session_state.get("last_team_colors", {})
    )

with col_clear:
    if st.button("🧹 Clear Table"):
        st.session_state.table_df = pd.DataFrame(columns=["Player", "Character"])
        st.session_state.pop("last_bracket", None)
        st.session_state.pop("r1_winners", None)
        st.rerun()

st.caption("Regular uses balanced randomization; Teams forbids same-team R1. Add an 'images/' folder with character PNGs to show icons.")
