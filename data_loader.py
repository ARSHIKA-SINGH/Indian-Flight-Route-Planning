
## Additional Utility File: `data_loader.py`
import json
import csv

class DataLoader:
    @staticmethod
    def load_airports_from_csv(planner, filename):
        """Load airports from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    planner.add_airport(
                        row['code'],
                        row['name'],
                        row['city'],
                        row['country']
                    )
            return True
        except Exception as e:
            print(f"Error loading airports: {e}")
            return False
    
    @staticmethod
    def load_routes_from_csv(planner, filename):
        """Load flight routes from CSV file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    planner.add_flight_route(
                        row['source'],
                        row['destination'],
                        int(row['distance']),
                        int(row['duration']),
                        float(row['cost']),
                        row.get('airline', 'Unknown')
                    )
            return True
        except Exception as e:
            print(f"Error loading routes: {e}")
            return False
    
    @staticmethod
    def export_network(planner, filename):
        """Export current network to JSON"""
        data = {
            'airports': planner.airports,
            'routes': planner.flight_routes
        }
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
    
    @staticmethod
    def import_network(planner, filename):
        """Import network from JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                planner.airports = data['airports']
                planner.flight_routes = data['routes']
            return True
        except Exception as e:
            print(f"Error importing network: {e}")
            return False