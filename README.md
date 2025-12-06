# ✈️ Flight Route Planner GUI  
### Floyd–Warshall Algorithm | PyQt5 | Network Visualization

A **desktop-based Flight Route Planning System** built using **Python and PyQt5**, implementing the **Floyd–Warshall algorithm** to compute optimal flight routes across a network of airports.  
The application supports **single-route optimization**, **multi-city journeys**, **network analysis**, and **interactive graph visualization**.

---

## 📌 Project Highlights

✅ Graph-based flight network modeling  
✅ Optimal route computation (Distance / Duration / Cost)  
✅ Multi-city journey planning  
✅ Network connectivity analysis & hub detection  
✅ Interactive visualization using NetworkX & Matplotlib  
✅ Real-world inspired Indian domestic flight dataset  

---

## 🚀 Features

### 🛫 Route Planning
- Select source and destination airports
- Optimize routes based on:
  - 📏 Distance  
  - ⏱ Duration  
  - 💰 Cost  
- Displays:
  - Complete optimal path
  - Total distance, time, and cost
  - Number of flights

### 🌍 Multi-City Journey Planning
- Add multiple intermediate cities
- Automatically computes best routes between consecutive stops
- Summarizes:
  - Full route
  - Total journey distance, duration, and price

### 📊 Network Analysis
- Computes network connectivity metrics
- Calculates average distance, duration, and cost
- Identifies the **most central (optimal hub) airport**

### 🗺️ Network Visualization
- Directed graph representation of the flight network
- Highlights shortest paths dynamically
- Interactive and visually intuitive layout

### 📋 Data Management
- Tabular display of airports and flight routes
- Modular planner and loader architecture

---

## 🧠 Algorithm Used

### Floyd–Warshall Algorithm
- Computes **shortest paths between all pairs of airports**
- Time Complexity: **O(n³)**
- Supports optimization by:
  - Distance
  - Duration
  - Cost

---

## 🛠️ Tech Stack

- **Programming Language:** Python 3  
- **GUI Framework:** PyQt5  
- **Graph Algorithms:** NetworkX  
- **Visualization:** Matplotlib  
- **Numerical Computation:** NumPy  

---

## 📦 Installation

### ✅ Prerequisites
- Python **3.7 or higher**

### ✅ Install Dependencies

```bash
pip install -r requirements.txt
