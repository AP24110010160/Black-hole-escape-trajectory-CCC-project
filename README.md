# 🚀 Black Hole Escape Trajectory Planner

An interactive Python simulation that finds the **safest and minimum-fuel escape route** for a spaceship trapped near a black hole using **Dijkstra’s Algorithm**.

---

## 📌 Project Overview

This project models space as a **2D grid environment** with different zones like gravity fields, asteroids, wormholes, and nebulae.

The objective is to guide a spaceship from its starting position to a safe exit while minimizing fuel consumption.

The system compares:
- ✅ **Dijkstra’s Algorithm (Optimal Path)**
- ⚠️ **Greedy Algorithm (Naive Approach)**

---

## 🧠 Algorithms Used

### 🔹 Dijkstra’s Algorithm
- Finds the **shortest path based on fuel cost**
- Uses a **priority queue (min-heap)** for efficiency
- Guarantees optimal solution

### 🔸 Greedy Algorithm
- Moves directly toward the destination
- Ignores fuel cost
- Used for comparison to highlight inefficiency

---

## 🌌 Features

- 🛰️ Interactive space simulation
- 🗺️ Grid-based universe with realistic hazards
- ⚡ Fuel optimization using shortest path algorithm
- 🎯 Multiple difficulty levels (Easy / Medium / Hard / Custom)
- 📊 Performance comparison (Dijkstra vs Greedy)
- 🎨 Colored terminal visualization
- 🎥 Animated path traversal
- 📉 Fuel usage tracking with visual bar

---

## 🪐 Environment Representation

Each grid cell represents a space zone with different fuel costs:

| Zone Type        | Symbol | Fuel Cost |
|-----------------|--------|----------|
| Space           | ·      | 1        |
| High Gravity    | ▓      | 15       |
| Medium Gravity  | ▒      | 8        |
| Low Gravity     | ░      | 4        |
| Asteroid        | ✦      | Blocked  |
| Nebula          | ~      | 6        |
| Wormhole        | ⊕      | 0        |
| Safe Zone       | ○      | 1        |

---

## ⚙️ How It Works

1. A grid map is generated with:
   - Black hole at the center
   - Gravity zones based on distance
   - Obstacles (asteroids)
   - Special zones (wormholes, safe areas)

2. User selects fuel budget (difficulty level)

3. Algorithms execute:
   - Dijkstra → finds optimal path
   - Greedy → finds faster but inefficient path

4. Results displayed:
   - Fuel consumption
   - Steps taken
   - Efficiency comparison
   - Mission success/failure

---

## 🖥️ Installation & Run

### 📦 Requirements
- Python 3.x

### ▶️ Run the Project
```bash
python main.py
