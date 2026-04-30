# ================================================================
#  🚀 BLACK HOLE ESCAPE TRAJECTORY PLANNER
#  Algorithm: Dijkstra's Shortest Path + Greedy Fuel Optimization
#  Find the safest, minimum-fuel escape route from a black hole
# ================================================================

import heapq
import random
import time
import math

# ── TERMINAL COLORS ─────────────────────────────────────────────
class C:
    BLACK   = '\033[30m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    PURPLE  = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    BLINK   = '\033[5m'
    RESET   = '\033[0m'
    BG_RED  = '\033[41m'
    BG_BLUE = '\033[44m'

def green(t):   return f"{C.GREEN}{t}{C.RESET}"
def yellow(t):  return f"{C.YELLOW}{t}{C.RESET}"
def red(t):     return f"{C.RED}{t}{C.RESET}"
def cyan(t):    return f"{C.CYAN}{t}{C.RESET}"
def purple(t):  return f"{C.PURPLE}{t}{C.RESET}"
def blue(t):    return f"{C.BLUE}{t}{C.RESET}"
def bold(t):    return f"{C.BOLD}{t}{C.RESET}"
def dim(t):     return f"{C.DIM}{t}{C.RESET}"
def white(t):   return f"{C.WHITE}{t}{C.RESET}"


# ================================================================
#  SPACE GRID CONFIGURATION
#  The universe is modeled as a GRID of nodes
#  Each node has a fuel cost to travel through it
#  based on proximity to the black hole and hazards
# ================================================================

# Grid size
ROWS = 12
COLS = 20

# Special characters for the map
TILE = {
    "space":       "·",
    "black_hole":  "◉",
    "gravity_high":"▓",
    "gravity_med": "▒",
    "gravity_low": "░",
    "asteroid":    "✦",
    "nebula":      "~",
    "safe_zone":   "○",
    "wormhole":    "⊕",
    "ship":        "▶",
    "exit":        "★",
    "path":        "•",
    "visited":     "·",
}

# Fuel costs for each zone type
FUEL_COST = {
    "space":       1,
    "gravity_high":15,
    "gravity_med": 8,
    "gravity_low": 4,
    "asteroid":    999,   # impassable
    "nebula":      6,
    "safe_zone":   1,
    "wormhole":    0,     # free travel
    "path":        1,
}

# Colors for each tile type
TILE_COLOR = {
    "space":       C.DIM + C.WHITE,
    "black_hole":  C.BOLD + C.RED,
    "gravity_high":C.RED,
    "gravity_med": C.YELLOW,
    "gravity_low": C.YELLOW + C.DIM,
    "asteroid":    C.WHITE + C.BOLD,
    "nebula":      C.PURPLE,
    "safe_zone":   C.GREEN + C.DIM,
    "wormhole":    C.CYAN + C.BOLD,
    "ship":        C.GREEN + C.BOLD,
    "exit":        C.YELLOW + C.BOLD,
    "path":        C.CYAN,
}


# ================================================================
#  GENERATE THE SPACE MAP
# ================================================================
def generate_map(rows, cols, black_hole_pos, ship_pos, exit_pos, seed=42):
    random.seed(seed)
    grid = [["space"] * cols for _ in range(rows)]

    bhr, bhc = black_hole_pos

    # Place gravity wells around black hole
    for r in range(rows):
        for c in range(cols):
            dist = math.sqrt((r - bhr)**2 + (c - bhc)**2)
            if dist < 1.5:
                grid[r][c] = "black_hole"
            elif dist < 3.0:
                grid[r][c] = "gravity_high"
            elif dist < 5.0:
                grid[r][c] = "gravity_med"
            elif dist < 7.0:
                grid[r][c] = "gravity_low"

    # Place random asteroids (impassable)
    asteroid_positions = [
        (2, 5), (3, 5), (4, 5),
        (7, 8), (7, 9),
        (2, 13),(3, 13),
        (9, 4), (10, 4),
        (5, 15),(6, 15),(6, 16),
        (1, 17),(2, 17),
    ]
    for r, c in asteroid_positions:
        if grid[r][c] == "space" or grid[r][c] == "gravity_low":
            grid[r][c] = "asteroid"

    # Place nebula clouds
    nebula_positions = [
        (1, 7),(1, 8),(2, 8),
        (8, 12),(9, 12),(9, 13),
        (4, 17),(5, 17),
    ]
    for r, c in nebula_positions:
        if grid[r][c] == "space":
            grid[r][c] = "nebula"

    # Place wormholes (shortcuts)
    wormhole_positions = [(2, 10), (9, 16)]
    for r, c in wormhole_positions:
        if grid[r][c] == "space":
            grid[r][c] = "wormhole"

    # Place safe zones
    safe_positions = [
        (0, 14),(0, 15),(1, 14),(1, 15),
        (10, 17),(11, 17),(10, 18),(11, 18),
    ]
    for r, c in safe_positions:
        if 0 <= r < rows and 0 <= c < cols:
            grid[r][c] = "safe_zone"

    # Place ship and exit
    sr, sc = ship_pos
    er, ec = exit_pos
    grid[sr][sc] = "ship"
    grid[er][ec] = "exit"

    return grid


# ================================================================
#  PRINT THE SPACE MAP
# ================================================================
def print_map(grid, path=None, visited=None, title="SPACE MAP"):
    rows = len(grid)
    cols = len(grid[0])

    path_set    = set(path)    if path    else set()
    visited_set = set(visited) if visited else set()

    print()
    print(bold(cyan(f"  ┌─ {title} " + "─" * (cols * 2 - len(title) - 2) + "┐")))

    for r in range(rows):
        print(bold(cyan("  │")), end=" ")
        for c in range(cols):
            cell = grid[r][c]
            pos  = (r, c)

            if pos in path_set and cell not in ["ship", "exit", "black_hole"]:
                char  = TILE["path"]
                color = TILE_COLOR["path"]
            elif cell in TILE_COLOR:
                char  = TILE.get(cell, "·")
                color = TILE_COLOR[cell]
            else:
                char  = "·"
                color = C.DIM

            print(f"{color}{char}{C.RESET}", end=" ")

        print(bold(cyan("│")))

    print(bold(cyan("  └" + "─" * (cols * 2 + 1) + "┘")))

    # Legend
    print()
    print(dim("  Legend: ") +
          f"{TILE_COLOR['ship']}{TILE['ship']}{C.RESET}=Ship  " +
          f"{TILE_COLOR['exit']}{TILE['exit']}{C.RESET}=Exit  " +
          f"{TILE_COLOR['black_hole']}{TILE['black_hole']}{C.RESET}=BlackHole  " +
          f"{TILE_COLOR['gravity_high']}{TILE['gravity_high']}{C.RESET}=HighGravity  " +
          f"{TILE_COLOR['asteroid']}{TILE['asteroid']}{C.RESET}=Asteroid  " +
          f"{TILE_COLOR['wormhole']}{TILE['wormhole']}{C.RESET}=Wormhole  " +
          f"{TILE_COLOR['path']}{TILE['path']}{C.RESET}=Path"
    )


# ================================================================
#  🧠 DIJKSTRA'S ALGORITHM
#  Find minimum fuel path from ship to exit
#  Nodes = grid cells
#  Edge weight = fuel cost of destination cell
# ================================================================
def dijkstra(grid, start, end):
    rows = len(grid)
    cols = len(grid[0])

    # Distance table: fuel cost to reach each cell
    dist = [[float('inf')] * cols for _ in range(rows)]
    prev = [[None] * cols for _ in range(rows)]

    sr, sc = start
    dist[sr][sc] = 0

    # Priority queue: (fuel_cost, row, col)
    pq = [(0, sr, sc)]
    visited = set()

    # Directions: up, down, left, right, diagonals
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    nodes_explored = 0

    while pq:
        fuel, r, c = heapq.heappop(pq)

        if (r, c) in visited:
            continue
        visited.add((r, c))
        nodes_explored += 1

        # Reached the exit!
        if (r, c) == end:
            break

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if (nr, nc) in visited:
                continue

            cell = grid[nr][nc]

            # Asteroids are impassable
            if cell == "asteroid":
                continue

            # Fuel cost to enter that cell
            move_cost = FUEL_COST.get(cell, 1)

            # Diagonal moves cost slightly more
            if dr != 0 and dc != 0:
                move_cost = int(move_cost * 1.4)

            new_fuel = fuel + move_cost

            if new_fuel < dist[nr][nc]:
                dist[nr][nc] = new_fuel
                prev[nr][nc] = (r, c)
                heapq.heappush(pq, (new_fuel, nr, nc))

    # Reconstruct path
    path = []
    er, ec = end
    if dist[er][ec] == float('inf'):
        return None, float('inf'), nodes_explored, visited

    cur = end
    while cur is not None:
        path.append(cur)
        r, c = cur
        cur = prev[r][c]

    path.reverse()
    return path, dist[er][ec], nodes_explored, visited


# ================================================================
#  🟡 GREEDY PATH (for comparison)
#  Always move toward the exit — ignores fuel costs
#  Shows WHY Dijkstra is better
# ================================================================
def greedy_path(grid, start, end):
    rows = len(grid)
    cols = len(grid[0])

    path      = [start]
    visited   = set([start])
    total_fuel = 0
    cur       = start

    directions = [
        (-1, 0),(1, 0),(0, -1),(0, 1),
        (-1,-1),(-1,1),(1,-1),(1,1)
    ]

    er, ec = end
    max_steps = rows * cols

    for _ in range(max_steps):
        if cur == end:
            break

        r, c = cur
        best_next = None
        best_dist = float('inf')

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if (nr, nc) in visited:
                continue
            cell = grid[nr][nc]
            if cell == "asteroid":
                continue

            # Greedy: pick cell closest to exit (ignores fuel)
            d = math.sqrt((nr - er)**2 + (nc - ec)**2)
            if d < best_dist:
                best_dist = d
                best_next = (nr, nc)

        if best_next is None:
            break

        nr, nc   = best_next
        cell     = grid[nr][nc]
        fuel_used = FUEL_COST.get(cell, 1)
        total_fuel += fuel_used
        path.append(best_next)
        visited.add(best_next)
        cur = best_next

    return path, total_fuel


# ================================================================
#  FUEL BAR
# ================================================================
def fuel_bar(used, total_fuel_start, width=35):
    if total_fuel_start == 0:
        pct = 0
    else:
        pct = min(used / total_fuel_start, 1.0)

    remaining_pct = 1.0 - pct
    filled  = int(remaining_pct * width)
    empty   = width - filled

    if remaining_pct > 0.6:
        color = C.GREEN
    elif remaining_pct > 0.3:
        color = C.YELLOW
    else:
        color = C.RED

    bar = f"{color}{'█' * filled}{C.RESET}{C.DIM}{'░' * empty}{C.RESET}"
    return f"[{bar}] {remaining_pct * 100:.1f}% remaining"


# ================================================================
#  ANIMATED PATH REVEAL
# ================================================================
def animate_path(grid, path, title, delay=0.05):
    print(f"\n  {bold(cyan(title))}")
    time.sleep(0.3)
    for i in range(1, len(path) + 1):
        print_map(grid, path=path[:i], title=title)
        if i < len(path):
            print(f"\r  {dim(f'Step {i}/{len(path)-1}...')}", end="", flush=True)
            time.sleep(delay)


# ================================================================
#  PRINT SECTION
# ================================================================
def print_section(title):
    print()
    print(bold(f"── {title} " + "─" * (55 - len(title))))

def print_header():
    print()
    print(bold(red  ("  ██████╗ ██╗      █████╗  ██████╗██╗  ██╗")))
    print(bold(red  ("  ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝")))
    print(bold(yellow("  ██████╔╝██║     ███████║██║     █████╔╝ ")))
    print(bold(yellow("  ██╔══██╗██║     ██╔══██║██║     ██╔═██╗ ")))
    print(bold(white ("  ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗")))
    print(bold(white ("  ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝")))
    print()
    print(bold(cyan  ("  🚀  BLACK HOLE ESCAPE TRAJECTORY PLANNER")))
    print(bold(cyan  ("  Dijkstra's Shortest Path + Greedy Navigation")))
    print(bold(cyan  ("  =" * 32)))
    print()


# ================================================================
#  MAIN PROGRAM
# ================================================================
def main():
    print_header()

    # ── MISSION BRIEFING ────────────────────────────────────────
    print_section("📡 MISSION BRIEFING")
    print(f"  {bold(red('ALERT:'))} Spaceship {cyan('ARES-7')} is trapped near a black hole!")
    print(f"  Black Hole : {red('SAGITTARIUS-X')} — Mass: 4.1 million solar masses")
    print(f"  Ship Fuel  : Limited — every wrong move costs precious fuel")
    print(f"  Mission    : Find the {green('minimum-fuel escape trajectory')}")
    print(f"  Algorithm  : {cyan('Dijkstra')} finds optimal path | {yellow('Greedy')} for comparison")
    print()
    print(dim("  The universe is modeled as a grid. Each zone has a fuel cost:"))
    print(f"  {red('▓')} High Gravity (15)  {yellow('▒')} Med Gravity (8)  "
          f"{dim('░')} Low Gravity (4)")
    print(f"  {white('✦')} Asteroid (blocked)  {purple('~')} Nebula (6)  "
          f"{cyan('⊕')} Wormhole (FREE!)")

    # ── CHOOSE DIFFICULTY ───────────────────────────────────────
    print_section("⚙️  MISSION PARAMETERS")
    print(dim("  [1] Easy    — Budget: 120 fuel units  (forgiving route)"))
    print(dim("  [2] Medium  — Budget: 90  fuel units  (careful planning needed)"))
    print(dim("  [3] Hard    — Budget: 60  fuel units  (near-impossible!)"))
    print(dim("  [4] Custom  — Enter your own fuel budget"))
    print()

    while True:
        try:
            choice = input(bold("  Choose difficulty (1-4): ")).strip()
            if choice == '1':
                fuel_budget = 120
                diff = "EASY"
            elif choice == '2':
                fuel_budget = 90
                diff = "MEDIUM"
            elif choice == '3':
                fuel_budget = 60
                diff = "HARD"
            elif choice == '4':
                fuel_budget = int(input(bold("  Enter fuel budget: ")))
                diff = "CUSTOM"
            else:
                print(red("  Enter 1, 2, 3 or 4"))
                continue
            break
        except ValueError:
            print(red("  Enter a valid number"))

    # ── MAP SETUP ───────────────────────────────────────────────
    black_hole = (5, 4)    # center of the black hole
    ship_pos   = (10, 1)   # spaceship starting position
    exit_pos   = (1, 18)   # escape point (top-right)

    grid = generate_map(ROWS, COLS, black_hole, ship_pos, exit_pos)

    print()
    print(f"  Difficulty     : {bold(yellow(diff))}")
    print(f"  Fuel Budget    : {bold(green(str(fuel_budget)))} units")
    print(f"  Ship Position  : {cyan(str(ship_pos))}")
    print(f"  Exit Position  : {yellow(str(exit_pos))}")
    print(f"  Black Hole     : {red(str(black_hole))}")

    # ── SHOW INITIAL MAP ────────────────────────────────────────
    print_map(grid, title="INITIAL MAP — FIND THE ESCAPE ROUTE")

    input(bold(f"\n  🚀 Press Enter to launch Dijkstra's Algorithm..."))

    # ── RUN DIJKSTRA ────────────────────────────────────────────
    print()
    print(bold(cyan("  ⚡ Running Dijkstra's Algorithm...")))
    time.sleep(0.5)

    dijk_path, dijk_fuel, nodes_explored, visited_nodes = dijkstra(
        grid, ship_pos, exit_pos
    )

    # ── RUN GREEDY ──────────────────────────────────────────────
    greedy_path_result, greedy_fuel = greedy_path(grid, ship_pos, exit_pos)

    # ── ANIMATE DIJKSTRA PATH ───────────────────────────────────
    if dijk_path:
        print()
        print(bold(green("  ✅ OPTIMAL ESCAPE TRAJECTORY FOUND!")))
        time.sleep(0.3)
        animate_path(grid, dijk_path,
                     title="DIJKSTRA OPTIMAL PATH", delay=0.08)
    else:
        print(bold(red("  ❌ NO ESCAPE ROUTE FOUND — Black hole gravity too strong!")))
        return

    # ── RESULTS ─────────────────────────────────────────────────
    print()
    print(bold(cyan("  " + "=" * 60)))
    print(bold(cyan("  🏁  MISSION RESULTS")))
    print(bold(cyan("  " + "=" * 60)))

    fuel_saved  = greedy_fuel - dijk_fuel
    efficiency  = (fuel_saved / greedy_fuel * 100) if greedy_fuel > 0 else 0
    mission_ok  = dijk_fuel <= fuel_budget

    print()
    print(f"  {bold('Algorithm'):<30} {bold('Fuel Used'):<15} {bold('Steps'):<10} {bold('Result')}")
    print(dim("  " + "─" * 65))
    print(f"  {cyan('Dijkstra (Optimal)'):<30} "
          f"{green(str(dijk_fuel)) + ' units':<23} "
          f"{str(len(dijk_path)-1):<10} "
          f"{green('✓ OPTIMAL')}")
    print(f"  {yellow('Greedy (Naive)'):<30} "
          f"{yellow(str(greedy_fuel)) + ' units':<23} "
          f"{str(len(greedy_path_result)-1):<10} "
          f"{red('✗ SUBOPTIMAL')}")

    print()
    print(f"  {bold('Fuel Budget')}       : {cyan(str(fuel_budget))} units")
    print(f"  {bold('Dijkstra Used')}     : {green(str(dijk_fuel))} units")
    print(f"  {bold('Greedy Used')}       : {yellow(str(greedy_fuel))} units")
    print(f"  {bold('Fuel Saved')}        : {green(str(fuel_saved))} units "
          f"{dim(f'({efficiency:.1f}% more efficient)')}")
    print(f"  {bold('Nodes Explored')}    : {dim(str(nodes_explored))}")
    print(f"  {bold('Path Length')}       : {dim(str(len(dijk_path)-1))} steps")

    # Fuel bar
    print()
    print(f"  Fuel Remaining : {fuel_bar(dijk_fuel, fuel_budget)}")

    # Mission status
    print()
    if mission_ok:
        print(bold(green("  " + "=" * 55)))
        print(bold(green(f"  ✅  MISSION SUCCESS — ARES-7 HAS ESCAPED! 🚀")))
        print(bold(green(f"  Fuel used: {dijk_fuel}/{fuel_budget} — "
                         f"{fuel_budget - dijk_fuel} units to spare!")))
        print(bold(green("  " + "=" * 55)))
    else:
        print(bold(red("  " + "=" * 55)))
        print(bold(red(f"  ❌  MISSION FAILED — NOT ENOUGH FUEL!")))
        print(bold(red(f"  Needed {dijk_fuel} units but only had {fuel_budget}.")))
        print(bold(red(f"  Try a higher difficulty budget or different route.")))
        print(bold(red("  " + "=" * 55)))

    # ── ALGORITHM INFO ──────────────────────────────────────────
    print_section("📊 ALGORITHM INFO")
    print(f"  {bold('Algorithm 1')}    : {cyan('Dijkstra Shortest Path')}")
    print(f"  {bold('Algorithm 2')}    : {yellow('Greedy Best-First Navigation')}")
    print(f"  {bold('Grid Size')}      : {dim(f'{ROWS} × {COLS} = {ROWS*COLS} nodes')}")
    print(f"  {bold('Time Complexity')}: {dim('O((V + E) log V) — Dijkstra with Min-Heap')}")
    print(f"  {bold('Space Complexity')}: {dim(f'O(V) = O({ROWS*COLS})')}")
    print(f"  {bold('Edge Weight')}    : {dim('Fuel cost of destination cell')}")
    print(f"  {bold('Directions')}     : {dim('8-directional movement (including diagonals)')}")

    # ── STEP-BY-STEP PATH ───────────────────────────────────────
    print_section("🗺️  STEP-BY-STEP ESCAPE TRAJECTORY")
    print(f"  {'Step':<6} {'Position':<14} {'Zone':<18} {'Fuel Cost':<12} {'Total Fuel'}")
    print(dim("  " + "─" * 62))

    cumulative = 0
    for i, (r, c) in enumerate(dijk_path):
        cell = grid[r][c]
        if cell in ["ship", "path"]:
            cell = "space"
        if (r, c) == ship_pos:
            cell = "ship"
        if (r, c) == exit_pos:
            cell = "exit"

        step_cost  = FUEL_COST.get(cell, 1) if i > 0 else 0
        cumulative += step_cost
        zone_color  = TILE_COLOR.get(cell, C.WHITE)

        if i == 0:
            label = green("START")
        elif (r, c) == exit_pos:
            label = yellow("EXIT ★")
        else:
            label = dim(str(i))

        print(f"  {label:<14} ({r:>2},{c:>2})       "
              f"{zone_color}{cell:<18}{C.RESET} "
              f"{str(step_cost):<12} {str(cumulative)}")

    # ── GREEDY vs DIJKSTRA COMPARISON ───────────────────────────
    print_section("⚡ WHY DIJKSTRA BEATS GREEDY")
    print(f"  Greedy always moves {yellow('toward the exit')} — looks smart but...")
    print(f"  It flies straight through {red('high-gravity zones')} near the black hole!")
    print(f"  Dijkstra explores {cyan('all possible routes')} and picks the cheapest.")
    print()
    print(f"  {bold('Greedy fuel')}    : {red(str(greedy_fuel))} units  "
          f"— {red('crashes through gravity wells')}")
    print(f"  {bold('Dijkstra fuel')} : {green(str(dijk_fuel))} units  "
          f"— {green('smart detour saves fuel')}")
    print(f"  {bold('Fuel saved')}     : {green(str(fuel_saved))} units  "
          f"— {green(f'{efficiency:.1f}% more efficient!')}")

    print()
    print(bold(cyan("  " + "=" * 60)))
    print(bold(cyan("  🚀 ARES-7 Mission Complete — Push to GitHub!")))
    print(bold(cyan("  " + "=" * 60)))
    print()


# ── Entry Point ──────────────────────────────────────────────────
if __name__ == '__main__':
    main()