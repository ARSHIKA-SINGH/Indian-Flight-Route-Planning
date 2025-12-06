import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, 
                             QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox,
                             QSpinBox, QDoubleSpinBox, QMessageBox, QHeaderView,
                             QSplitter, QFrame, QProgressBar, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import networkx as nx
import random

class FlightRoutePlanner:
    def __init__(self):
        self.airports = {}
        self.flight_routes = []
        self.distance_matrix = []
        self.next_node = []
        self.airport_index_map = {}
        self.index_airport_map = {}
    
    def add_airport(self, code: str, name: str, city: str, country: str):
        self.airports[code] = {'name': name, 'city': city, 'country': country}
    
    def add_flight_route(self, source: str, destination: str, distance: int, 
                        duration: int, cost: float, airline: str = "Unknown"):
        self.flight_routes.append({
            'source': source, 'destination': destination, 'distance': distance,
            'duration': duration, 'cost': cost, 'airline': airline
        })
    
    def build_graph(self, weight_type: str = 'distance'):
        airports_list = list(self.airports.keys())
        n = len(airports_list)
        
        self.airport_index_map = {code: idx for idx, code in enumerate(airports_list)}
        self.index_airport_map = {idx: code for idx, code in enumerate(airports_list)}
        
        self.distance_matrix = [[float('inf')] * n for _ in range(n)]
        self.next_node = [[-1] * n for _ in range(n)]
        
        for i in range(n):
            self.distance_matrix[i][i] = 0
            self.next_node[i][i] = i
        
        for route in self.flight_routes:
            src_idx = self.airport_index_map[route['source']]
            dest_idx = self.airport_index_map[route['destination']]
            
            weight = route[weight_type]
            
            if weight < self.distance_matrix[src_idx][dest_idx]:
                self.distance_matrix[src_idx][dest_idx] = weight
                self.next_node[src_idx][dest_idx] = dest_idx
    
    def floyd_warshall(self, weight_type: str = 'distance'):
        self.build_graph(weight_type)
        n = len(self.distance_matrix)
        
        for k in range(n):
            for i in range(n):
                if self.distance_matrix[i][k] != float('inf'):
                    for j in range(n):
                        if (self.distance_matrix[k][j] != float('inf') and 
                            self.distance_matrix[i][j] > self.distance_matrix[i][k] + self.distance_matrix[k][j]):
                            
                            self.distance_matrix[i][j] = self.distance_matrix[i][k] + self.distance_matrix[k][j]
                            self.next_node[i][j] = self.next_node[i][k]
        
        return self.distance_matrix
    
    def get_shortest_path(self, source: str, destination: str):
        if source not in self.airport_index_map or destination not in self.airport_index_map:
            return {"error": "Airport not found"}
        
        src_idx = self.airport_index_map[source]
        dest_idx = self.airport_index_map[destination]
        
        if self.distance_matrix[src_idx][dest_idx] == float('inf'):
            return {"error": "No path exists between the airports"}
        
        path = []
        current = src_idx
        
        while current != dest_idx:
            path.append(self.index_airport_map[current])
            current = self.next_node[current][dest_idx]
        
        path.append(self.index_airport_map[dest_idx])
        
        total_distance = 0
        total_duration = 0
        total_cost = 0
        
        for i in range(len(path) - 1):
            src_airport = path[i]
            dest_airport = path[i + 1]
            
            for route in self.flight_routes:
                if route['source'] == src_airport and route['destination'] == dest_airport:
                    total_distance += route['distance']
                    total_duration += route['duration']
                    total_cost += route['cost']
                    break
        
        return {
            'path': path,
            'total_distance': total_distance,
            'total_duration': total_duration,
            'total_cost': round(total_cost, 2),
            'number_of_flights': len(path) - 1
        }

class NetworkGraph(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.planner = None
    
    def plot_network(self, planner, highlight_path=None):
        self.planner = planner
        self.ax.clear()
        
        G = nx.DiGraph()
        
        # Add nodes
        for airport_code, airport_info in planner.airports.items():
            G.add_node(airport_code, 
                      city=airport_info['city'], 
                      country=airport_info['country'])
        
        # Add edges
        for route in planner.flight_routes:
            G.add_edge(route['source'], route['destination'],
                      distance=route['distance'],
                      duration=route['duration'],
                      cost=route['cost'],
                      airline=route['airline'])
        
        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        node_colors = ['lightblue' for _ in G.nodes()]
        node_sizes = [800 for _ in G.nodes()]
        
        if highlight_path:
            for i, node in enumerate(highlight_path):
                node_colors[list(G.nodes()).index(node)] = 'red'
                node_sizes[list(G.nodes()).index(node)] = 1200
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.9)
        
        # Draw edges
        edge_colors = ['gray' for _ in G.edges()]
        edge_widths = [1 for _ in G.edges()]
        
        if highlight_path:
            for i in range(len(highlight_path) - 1):
                edge_idx = list(G.edges()).index((highlight_path[i], highlight_path[i + 1]))
                edge_colors[edge_idx] = 'red'
                edge_widths[edge_idx] = 3
        
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, 
                              width=edge_widths, alpha=0.7, 
                              arrows=True, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        # Draw edge labels
        edge_labels = {(u, v): f"{d['distance']}km" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
        
        self.ax.set_title("Indian Domestic Flight Network", fontsize=14, fontweight='bold')
        self.ax.axis('off')
        self.fig.tight_layout()
        self.draw()

class AirportTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Code", "Name", "City", "Country"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def update_data(self, airports):
        self.setRowCount(len(airports))
        for row, (code, info) in enumerate(airports.items()):
            self.setItem(row, 0, QTableWidgetItem(code))
            self.setItem(row, 1, QTableWidgetItem(info['name']))
            self.setItem(row, 2, QTableWidgetItem(info['city']))
            self.setItem(row, 3, QTableWidgetItem(info['country']))

class RoutesTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["From", "To", "Distance (km)", "Time (min)", "Price (₹)", "Airline"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def update_data(self, routes):
        self.setRowCount(len(routes))
        for row, route in enumerate(routes):
            self.setItem(row, 0, QTableWidgetItem(route['source']))
            self.setItem(row, 1, QTableWidgetItem(route['destination']))
            self.setItem(row, 2, QTableWidgetItem(str(route['distance'])))
            self.setItem(row, 3, QTableWidgetItem(str(route['duration'])))
            self.setItem(row, 4, QTableWidgetItem("₹" + str(route['cost'])))
            self.setItem(row, 5, QTableWidgetItem(route['airline']))

class FlightPlannerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.planner = FlightRoutePlanner()
        self.init_ui()
        self.load_indian_airline_data()
        
    def init_ui(self):
        self.setWindowTitle("Indian Flight Route Planner - Floyd-Warshall Algorithm")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title with Indian theme colors
        title = QLabel("✈️ Indian Flight Route Planning System")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 15px; background-color: #FF9933; color: white; border-radius: 10px;")
        main_layout.addWidget(title)
        
        # Create tabs
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Add tabs
        tabs.addTab(self.create_route_planning_tab(), "Route Planning")
        tabs.addTab(self.create_network_analysis_tab(), "Network Analysis")
        tabs.addTab(self.create_data_management_tab(), "Data Management")
        tabs.addTab(self.create_visualization_tab(), "Network Map")
        
        # Status bar
        self.statusBar().showMessage("Ready to compute optimal flight routes across India")
    
    def create_route_planning_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Input section
        input_group = QGroupBox("Route Planning Parameters")
        input_layout = QHBoxLayout(input_group)
        
        # Source selection
        input_layout.addWidget(QLabel("From:"))
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(150)
        input_layout.addWidget(self.source_combo)
        
        input_layout.addWidget(QLabel("To:"))
        self.dest_combo = QComboBox()
        self.dest_combo.setMinimumWidth(150)
        input_layout.addWidget(self.dest_combo)
        
        # Optimization criteria
        input_layout.addWidget(QLabel("Optimize for:"))
        self.criteria_combo = QComboBox()
        self.criteria_combo.addItems(["Distance", "Duration", "Cost"])
        input_layout.addWidget(self.criteria_combo)
        
        # Find route button
        self.find_route_btn = QPushButton("Find Optimal Route")
        self.find_route_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; }")
        self.find_route_btn.clicked.connect(self.find_optimal_route)
        input_layout.addWidget(self.find_route_btn)
        
        layout.addWidget(input_group)
        
        # Results section
        results_group = QGroupBox("Route Details")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMinimumHeight(200)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Multi-city planning
        multi_city_group = QGroupBox("Multi-City Journey Planning")
        multi_city_layout = QVBoxLayout(multi_city_group)
        
        # City list
        city_input_layout = QHBoxLayout()
        city_input_layout.addWidget(QLabel("Add city:"))
        self.city_combo = QComboBox()
        city_input_layout.addWidget(self.city_combo)
        
        self.add_city_btn = QPushButton("Add to Journey")
        self.add_city_btn.clicked.connect(self.add_city_to_journey)
        city_input_layout.addWidget(self.add_city_btn)
        
        self.clear_journey_btn = QPushButton("Clear Journey")
        self.clear_journey_btn.clicked.connect(self.clear_journey)
        city_input_layout.addWidget(self.clear_journey_btn)
        
        multi_city_layout.addLayout(city_input_layout)
        
        # Journey list
        self.journey_list = QListWidget()
        multi_city_layout.addWidget(self.journey_list)
        
        # Plan journey button
        self.plan_journey_btn = QPushButton("Plan Multi-City Journey")
        self.plan_journey_btn.setStyleSheet("QPushButton { background-color: #e67e22; color: white; font-weight: bold; padding: 8px; }")
        self.plan_journey_btn.clicked.connect(self.plan_multi_city_journey)
        multi_city_layout.addWidget(self.plan_journey_btn)
        
        layout.addWidget(multi_city_group)
        
        return widget
    
    def create_network_analysis_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analysis controls
        controls_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("Run Network Analysis")
        self.analyze_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 8px; }")
        self.analyze_btn.clicked.connect(self.run_network_analysis)
        controls_layout.addWidget(self.analyze_btn)
        
        self.find_hub_btn = QPushButton("Find Optimal Hub")
        self.find_hub_btn.clicked.connect(self.find_optimal_hub)
        controls_layout.addWidget(self.find_hub_btn)
        
        layout.addLayout(controls_layout)
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)
        
        return widget
    
    def create_data_management_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Airport management
        airport_group = QGroupBox("Indian Airports")
        airport_layout = QVBoxLayout(airport_group)
        
        self.airport_table = AirportTable()
        airport_layout.addWidget(self.airport_table)
        
        layout.addWidget(airport_group)
        
        # Routes management
        routes_group = QGroupBox("Domestic Flight Routes")
        routes_layout = QVBoxLayout(routes_group)
        
        self.routes_table = RoutesTable()
        routes_layout.addWidget(self.routes_table)
        
        layout.addWidget(routes_group)
        
        return widget
    
    def create_visualization_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Visualization controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Highlight Route:"))
        
        self.viz_source_combo = QComboBox()
        self.viz_dest_combo = QComboBox()
        self.plot_route_btn = QPushButton("Plot Route")
        self.plot_route_btn.clicked.connect(self.plot_specific_route)
        
        controls_layout.addWidget(self.viz_source_combo)
        controls_layout.addWidget(QLabel("to"))
        controls_layout.addWidget(self.viz_dest_combo)
        controls_layout.addWidget(self.plot_route_btn)
        
        controls_layout.addStretch()
        
        self.refresh_viz_btn = QPushButton("Refresh Visualization")
        self.refresh_viz_btn.clicked.connect(self.refresh_visualization)
        controls_layout.addWidget(self.refresh_viz_btn)
        
        layout.addLayout(controls_layout)
        
        # Network graph
        self.network_graph = NetworkGraph(self, width=10, height=8)
        layout.addWidget(self.network_graph)
        
        return widget
    
    def load_indian_airline_data(self):
        """Load Indian airports and domestic flight routes"""
        
        # Major Indian Airports
        indian_airports = [
            # Metro Cities
            ("DEL", "Indira Gandhi International", "Delhi", "India"),
            ("BOM", "Chhatrapati Shivaji Maharaj International", "Mumbai", "India"),
            ("MAA", "Chennai International", "Chennai", "India"),
            ("BLR", "Kempegowda International", "Bengaluru", "India"),
            ("HYD", "Rajiv Gandhi International", "Hyderabad", "India"),
            ("CCU", "Netaji Subhash Chandra Bose International", "Kolkata", "India"),
            
            # Other Major Cities
            ("AMD", "Sardar Vallabhbhai Patel International", "Ahmedabad", "India"),
            ("PNQ", "Pune International", "Pune", "India"),
            ("GOI", "Goa International", "Goa", "India"),
            ("COK", "Cochin International", "Kochi", "India"),
            ("TRV", "Trivandrum International", "Thiruvananthapuram", "India"),
            ("CCJ", "Calicut International", "Kozhikode", "India"),
            
            # Tourist Destinations
            ("JAI", "Jaipur International", "Jaipur", "India"),
            ("ATQ", "Sri Guru Ram Dass Jee International", "Amritsar", "India"),
            ("IXC", "Chandigarh International", "Chandigarh", "India"),
            ("GAU", "Lokpriya Gopinath Bordoloi International", "Guwahati", "India"),
            ("PAT", "Jay Prakash Narayan Airport", "Patna", "India"),
            ("LKO", "Chaudhary Charan Singh International", "Lucknow", "India"),
            
            # Additional Cities
            ("IXB", "Bagdogra Airport", "Siliguri", "India"),
            ("SXR", "Srinagar International", "Srinagar", "India"),
            ("VNS", "Lal Bahadur Shastri Airport", "Varanasi", "India"),
        ]
        
        for code, name, city, country in indian_airports:
            self.planner.add_airport(code, name, city, country)
        
        # Indian Domestic Airlines
        indian_airlines = [
            "IndiGo", "Air India", "SpiceJet", "Vistara", "Go First", 
            "AirAsia India", "Akasa Air", "Alliance Air"
        ]
        
        # Domestic Flight Routes with realistic distances and prices
        domestic_routes = [
            # Delhi Routes
            ("DEL", "BOM", 1150, 120, 4500, "IndiGo"),
            ("DEL", "BLR", 1750, 150, 5200, "Air India"),
            ("DEL", "MAA", 1760, 155, 5100, "SpiceJet"),
            ("DEL", "HYD", 1260, 125, 4300, "Vistara"),
            ("DEL", "CCU", 1305, 130, 4200, "IndiGo"),
            ("DEL", "AMD", 775, 85, 3200, "Go First"),
            ("DEL", "PNQ", 1160, 120, 4400, "AirAsia India"),
            ("DEL", "GOI", 1550, 140, 4800, "IndiGo"),
            ("DEL", "JAI", 260, 60, 2500, "SpiceJet"),
            ("DEL", "ATQ", 405, 70, 2800, "IndiGo"),
            ("DEL", "IXC", 240, 55, 2300, "Vistara"),
            ("DEL", "LKO", 425, 70, 2700, "SpiceJet"),
            ("DEL", "VNS", 680, 90, 3300, "Air India"),
            ("DEL", "SXR", 835, 100, 3800, "IndiGo"),
            
            # Mumbai Routes
            ("BOM", "BLR", 845, 105, 3800, "IndiGo"),
            ("BOM", "MAA", 1035, 115, 4100, "Air India"),
            ("BOM", "HYD", 515, 80, 2900, "Vistara"),
            ("BOM", "CCU", 1660, 145, 4900, "SpiceJet"),
            ("BOM", "AMD", 440, 75, 2700, "IndiGo"),
            ("BOM", "PNQ", 120, 45, 1800, "Go First"),
            ("BOM", "GOI", 410, 70, 2600, "AirAsia India"),
            ("BOM", "COK", 1050, 115, 4000, "IndiGo"),
            ("BOM", "JAI", 875, 100, 3500, "SpiceJet"),
            ("BOM", "TRV", 1250, 125, 4200, "Air India"),
            
            # Bengaluru Routes
            ("BLR", "HYD", 495, 75, 2800, "IndiGo"),
            ("BLR", "MAA", 285, 65, 2200, "SpiceJet"),
            ("BLR", "CCU", 1560, 140, 4700, "Air India"),
            ("BLR", "COK", 535, 80, 2900, "IndiGo"),
            ("BLR", "TRV", 600, 85, 3100, "Vistara"),
            ("BLR", "GOI", 430, 70, 2700, "AirAsia India"),
            ("BLR", "PNQ", 585, 85, 3000, "IndiGo"),
            ("BLR", "AMD", 1165, 120, 4100, "SpiceJet"),
            
            # Chennai Routes
            ("MAA", "HYD", 515, 80, 2900, "IndiGo"),
            ("MAA", "CCU", 1360, 130, 4300, "SpiceJet"),
            ("MAA", "COK", 595, 85, 3000, "Air India"),
            ("MAA", "TRV", 605, 85, 3100, "IndiGo"),
            ("MAA", "BLR", 285, 65, 2200, "SpiceJet"),
            ("MAA", "CCJ", 285, 65, 2300, "Air India"),
            
            # Kolkata Routes
            ("CCU", "HYD", 1190, 120, 4200, "IndiGo"),
            ("CCU", "GAU", 605, 85, 3200, "SpiceJet"),
            ("CCU", "PAT", 450, 75, 2700, "Air India"),
            ("CCU", "IXB", 375, 65, 2400, "IndiGo"),
            ("CCU", "DEL", 1305, 130, 4200, "Vistara"),
            ("CCU", "BOM", 1660, 145, 4900, "SpiceJet"),
            
            # Hyderabad Routes
            ("HYD", "GOI", 615, 85, 3100, "IndiGo"),
            ("HYD", "PNQ", 465, 75, 2800, "Vistara"),
            ("HYD", "COK", 865, 100, 3500, "Air India"),
            ("HYD", "BLR", 495, 75, 2800, "IndiGo"),
            
            # Goa Routes
            ("GOI", "COK", 485, 75, 2800, "Air India"),
            ("GOI", "BLR", 430, 70, 2700, "IndiGo"),
            ("GOI", "DEL", 1550, 140, 4800, "Vistara"),
            
            # Kerala Routes
            ("COK", "TRV", 175, 50, 2000, "IndiGo"),
            ("COK", "CCJ", 175, 50, 2100, "Air India"),
            ("COK", "BLR", 535, 80, 2900, "SpiceJet"),
            
            # Regional Routes
            ("JAI", "AMD", 560, 80, 2900, "IndiGo"),
            ("ATQ", "DEL", 405, 70, 2800, "SpiceJet"),
            ("LKO", "BOM", 1200, 125, 4100, "Air India"),
            ("PAT", "DEL", 850, 95, 3400, "IndiGo"),
            ("GAU", "CCU", 605, 85, 3200, "SpiceJet"),
            ("IXB", "CCU", 375, 65, 2400, "IndiGo"),
            ("SXR", "DEL", 835, 100, 3800, "Air India"),
            ("VNS", "DEL", 680, 90, 3300, "IndiGo"),
        ]
        
        # Add all routes (both directions)
        for src, dest, dist, dur, cost, airline in domestic_routes:
            self.planner.add_flight_route(src, dest, dist, dur, cost, airline)
            # Add return flight (slightly different price)
            self.planner.add_flight_route(dest, src, dist, dur, cost * 0.95, airline)
        
        # Update UI components
        self.update_ui_components()
        
        # Initial visualization
        self.refresh_visualization()
        
        self.statusBar().showMessage("Indian airline data loaded successfully")
    
    def update_ui_components(self):
        # Update combo boxes
        airport_codes = list(self.planner.airports.keys())
        
        for combo in [self.source_combo, self.dest_combo, self.viz_source_combo, self.viz_dest_combo, self.city_combo]:
            combo.clear()
            combo.addItems(airport_codes)
        
        # Update tables
        self.airport_table.update_data(self.planner.airports)
        self.routes_table.update_data(self.planner.flight_routes)
    
    def find_optimal_route(self):
        source = self.source_combo.currentText()
        destination = self.dest_combo.currentText()
        criteria = self.criteria_combo.currentText().lower()
        
        if source == destination:
            QMessageBox.warning(self, "Invalid Selection", "Please select different source and destination airports.")
            return
        
        # Show progress
        self.statusBar().showMessage(f"Computing optimal route from {source} to {destination}...")
        
        # Run Floyd-Warshall
        self.planner.floyd_warshall(criteria)
        
        # Get shortest path
        result = self.planner.get_shortest_path(source, destination)
        
        # Display results
        if 'error' in result:
            self.results_text.setText(f"Error: {result['error']}")
        else:
            output = f"🏆 OPTIMAL ROUTE FOUND!\n\n"
            output += f"📍 Route: {' → '.join(result['path'])}\n"
            output += f"📏 Total Distance: {result['total_distance']} km\n"
            output += f"⏱️ Total Duration: {result['total_duration']} minutes\n"
            output += f"💰 Total Cost: ₹{result['total_cost']}\n"
            output += f"✈️ Number of Flights: {result['number_of_flights']}\n\n"
            output += f"Optimization Criteria: {criteria.capitalize()}"
            
            self.results_text.setText(output)
            
            # Highlight route in visualization
            self.highlighted_path = result['path']
            self.refresh_visualization()
        
        self.statusBar().showMessage(f"Route computed from {source} to {destination}")
    
    def add_city_to_journey(self):
        city = self.city_combo.currentText()
        item = QListWidgetItem(f"📍 {city} - {self.planner.airports[city]['city']}")
        self.journey_list.addItem(item)
    
    def clear_journey(self):
        self.journey_list.clear()
    
    def plan_multi_city_journey(self):
        if self.journey_list.count() < 2:
            QMessageBox.warning(self, "Invalid Journey", "Please add at least 2 cities to plan a journey.")
            return
        
        cities = []
        for i in range(self.journey_list.count()):
            text = self.journey_list.item(i).text()
            city_code = text.split(' ')[1]
            cities.append(city_code)
        
        self.statusBar().showMessage("Planning multi-city journey...")
        
        # Simple implementation - connect cities in order
        total_distance = 0
        total_duration = 0
        total_cost = 0
        full_path = []
        
        output = "🌍 MULTI-CITY JOURNEY PLAN\n\n"
        
        for i in range(len(cities) - 1):
            source = cities[i]
            dest = cities[i + 1]
            
            self.planner.floyd_warshall('distance')  # Use distance for planning
            result = self.planner.get_shortest_path(source, dest)
            
            if 'error' in result:
                output += f"❌ Error from {source} to {dest}: {result['error']}\n"
                continue
            
            if i == 0:
                full_path.extend(result['path'])
            else:
                full_path.extend(result['path'][1:])
            
            total_distance += result['total_distance']
            total_duration += result['total_duration']
            total_cost += result['total_cost']
            
            output += f"Leg {i+1}: {source} → {dest}\n"
            output += f"  Route: {' → '.join(result['path'])}\n"
            output += f"  Distance: {result['total_distance']} km, "
            output += f"Duration: {result['total_duration']} min, "
            output += f"Cost: ₹{result['total_cost']}\n\n"
        
        output += f"📊 JOURNEY SUMMARY\n"
        output += f"Full Route: {' → '.join(full_path)}\n"
        output += f"Total Distance: {total_distance} km\n"
        output += f"Total Duration: {total_duration} minutes\n"
        output += f"Total Cost: ₹{total_cost:.2f}\n"
        output += f"Total Flights: {len(full_path) - 1}"
        
        self.results_text.setText(output)
        self.highlighted_path = full_path
        self.refresh_visualization()
        
        self.statusBar().showMessage("Multi-city journey planned successfully")
    
    def run_network_analysis(self):
        self.statusBar().showMessage("Analyzing Indian flight network...")
        
        # Run analysis for all criteria
        analysis_results = "📊 INDIAN FLIGHT NETWORK ANALYSIS\n\n"
        
        for criteria in ['distance', 'duration', 'cost']:
            self.planner.floyd_warshall(criteria)
            
            n = len(self.planner.distance_matrix)
            total_possible = n * (n - 1)
            connected_routes = sum(
                1 for i in range(n) for j in range(n) 
                if i != j and self.planner.distance_matrix[i][j] != float('inf')
            )
            
            analysis_results += f"Optimizing for {criteria.upper()}:\n"
            analysis_results += f"  • Connected routes: {connected_routes}/{total_possible} "
            analysis_results += f"({connected_routes/total_possible*100:.1f}%)\n"
            
            # Find average values
            total_distance = 0
            total_duration = 0
            total_cost = 0
            count = 0
            
            for i in range(n):
                for j in range(n):
                    if i != j and self.planner.distance_matrix[i][j] != float('inf'):
                        path_info = self.planner.get_shortest_path(
                            self.planner.index_airport_map[i],
                            self.planner.index_airport_map[j]
                        )
                        if 'path' in path_info:
                            total_distance += path_info['total_distance']
                            total_duration += path_info['total_duration']
                            total_cost += path_info['total_cost']
                            count += 1
            
            if count > 0:
                analysis_results += f"  • Average distance: {total_distance/count:.0f} km\n"
                analysis_results += f"  • Average duration: {total_duration/count:.0f} min\n"
                analysis_results += f"  • Average cost: ₹{total_cost/count:.0f}\n"
            
            analysis_results += "\n"
        
        self.analysis_text.setText(analysis_results)
        self.statusBar().showMessage("Network analysis completed")
    
    def find_optimal_hub(self):
        self.statusBar().showMessage("Finding optimal hub airport in India...")
        
        self.planner.floyd_warshall('distance')
        n = len(self.planner.distance_matrix)
        
        min_max_distance = float('inf')
        optimal_hub = ""
        
        for i in range(n):
            max_distance = max(self.planner.distance_matrix[i])
            if max_distance < float('inf') and max_distance < min_max_distance:
                min_max_distance = max_distance
                optimal_hub = self.planner.index_airport_map[i]
        
        hub_info = self.planner.airports[optimal_hub]
        result = f"🏆 OPTIMAL HUB AIRPORT IN INDIA\n\n"
        result += f"Airport: {optimal_hub}\n"
        result += f"Name: {hub_info['name']}\n"
        result += f"Location: {hub_info['city']}, {hub_info['country']}\n"
        result += f"Maximum distance to any reachable airport: {min_max_distance:.0f} km\n\n"
        result += f"This airport is the most centrally located in the Indian network, minimizing the maximum distance to all other airports."
        
        self.analysis_text.setText(result)
        self.statusBar().showMessage(f"Optimal hub found: {optimal_hub}")
    
    def plot_specific_route(self):
        source = self.viz_source_combo.currentText()
        destination = self.viz_dest_combo.currentText()
        
        if source == destination:
            QMessageBox.warning(self, "Invalid Selection", "Please select different source and destination airports.")
            return
        
        self.planner.floyd_warshall('distance')
        result = self.planner.get_shortest_path(source, destination)
        
        if 'path' in result:
            self.highlighted_path = result['path']
            self.refresh_visualization()
            self.statusBar().showMessage(f"Route {source} → {destination} highlighted on map")
        else:
            QMessageBox.warning(self, "No Route", f"No route found from {source} to {destination}")
    
    def refresh_visualization(self):
        if hasattr(self, 'highlighted_path'):
            self.network_graph.plot_network(self.planner, self.highlighted_path)
        else:
            self.network_graph.plot_network(self.planner)
        self.statusBar().showMessage("Indian flight network visualization updated")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = FlightPlannerGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()