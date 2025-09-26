import requests
import json
from datetime import datetime, timedelta
import os

class RouteOptimizer:
    def __init__(self):
        self.otp_url = "http://localhost:8081/otp/routers/default/plan"
        self.otp_base_url = "http://localhost:8081/otp/routers/default"
        self.stations = self.load_stations()
        self.train_fares = self.initialize_train_fares()
        
    def load_stations(self):
        """Load stations from OTP server or fallback to JSON file"""
        try:
            # First try to get stations from OTP server
            print("🌐 Attempting to load stations from OTP server...")
            otp_stations = self.fetch_otp_stations()
            if otp_stations:
                print(f"✅ Loaded {len(otp_stations)} stations from OTP server")
                return otp_stations
                
            # If OTP fails, try JSON file as fallback
            print("⚠️  OTP server not available, trying stations.json...")
            # Try different possible paths for stations.json
            possible_paths = [
                '../data/stations.json',
                './data/stations.json',
                'data/stations.json'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        print(f"✅ Loaded stations from: {path}")
                        # Convert JSON format to OTP format
                        converted_stations = []
                        for station in data:
                            if isinstance(station, dict) and 'label' in station and 'value' in station:
                                coords = station['value'].split(',')
                                if len(coords) == 2:
                                    converted_stations.append({
                                        'name': station['label'],
                                        'lat': float(coords[0]),
                                        'lng': float(coords[1]),
                                        'type': 'STATION'
                                    })
                        return converted_stations
            
            # If no file found, return mock data
            print("⚠️  stations.json not found, using mock data")
            return self.get_mock_stations()
            
        except Exception as e:
            print(f"❌ Error loading stations: {e}")
            return self.get_mock_stations()
    
    def initialize_train_fares(self):
        """Initialize Mumbai train fare data with station-to-station pricing"""
        return {
            # Western Railway (WR) - Key stations and their fare zones
            'WR': {
                'stations': [
                    'Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road', 
                    'Mumbai Central', 'Mahalaxmi', 'Lower Parel', 'Prabhadevi', 
                    'Dadar', 'Matunga', 'Mahim', 'Bandra', 'Khar Road', 'Santacruz',
                    'Vile Parle', 'Andheri', 'Jogeshwari', 'Ram Mandir', 'Goregaon',
                    'Malad', 'Kandivali', 'Borivali', 'Dahisar', 'Mira Road', 'Bhayandar',
                    'Naigaon', 'Vasai Road', 'Nallasopara', 'Virar'
                ],
                'fare_zones': {
                    # Distance-based fare zones for WR
                    ('Churchgate', 'Dadar'): {'2nd': 10, '1st': 40, 'AC': 50},
                    ('Churchgate', 'Andheri'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Churchgate', 'Borivali'): {'2nd': 20, '1st': 85, 'AC': 95},
                    ('Churchgate', 'Virar'): {'2nd': 25, '1st': 100, 'AC': 115},
                    ('Dadar', 'Andheri'): {'2nd': 10, '1st': 35, 'AC': 45},
                    ('Dadar', 'Borivali'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Dadar', 'Virar'): {'2nd': 20, '1st': 85, 'AC': 95},
                    ('Andheri', 'Borivali'): {'2nd': 10, '1st': 30, 'AC': 40},
                    ('Andheri', 'Virar'): {'2nd': 15, '1st': 55, 'AC': 65},
                    ('Borivali', 'Virar'): {'2nd': 10, '1st': 25, 'AC': 35}
                }
            },
            # Central Railway (CR) - Main line stations
            'CR': {
                'stations': [
                    'CSMT', 'Masjid', 'Sandhurst Road', 'Dockyard Road', 'Reay Road',
                    'Cotton Green', 'Sewri', 'Wadala', 'King Circle', 'Mahim',
                    'Dadar', 'Matunga', 'Sion', 'Kurla', 'Vidyavihar', 'Ghatkopar',
                    'Vikhroli', 'Kanjurmarg', 'Bhandup', 'Nahur', 'Mulund',
                    'Thane', 'Kalwa', 'Mumbra', 'Diva', 'Kopar', 'Dombivli',
                    'Thakurli', 'Kalyan', 'Vithalwadi', 'Ulhasnagar', 'Ambernath'
                ],
                'fare_zones': {
                    ('CSMT', 'Dadar'): {'2nd': 5, '1st': 25, 'AC': 35},
                    ('CSMT', 'Kurla'): {'2nd': 10, '1st': 50, 'AC': 70},
                    ('CSMT', 'Thane'): {'2nd': 15, '1st': 85, 'AC': 95},
                    ('CSMT', 'Kalyan'): {'2nd': 20, '1st': 100, 'AC': 105},
                    ('Dadar', 'Kurla'): {'2nd': 5, '1st': 20, 'AC': 30},
                    ('Dadar', 'Thane'): {'2nd': 10, '1st': 45, 'AC': 55},
                    ('Dadar', 'Kalyan'): {'2nd': 15, '1st': 70, 'AC': 80},
                    ('Kurla', 'Thane'): {'2nd': 10, '1st': 35, 'AC': 45},
                    ('Kurla', 'Kalyan'): {'2nd': 15, '1st': 60, 'AC': 70},
                    ('Thane', 'Kalyan'): {'2nd': 10, '1st': 30, 'AC': 40}
                }
            },
            # Harbour Railway (HR) - CSMT to Panvel line
            'HR': {
                'stations': [
                    'CSMT', 'Dockyard Road', 'Reay Road', 'Cotton Green', 'Sewri',
                    'Wadala', 'King Circle', 'Kurla', 'Chunabhatti', 'Tilak Nagar',
                    'Chembur', 'Govandi', 'Mankhurd', 'Vashi', 'Sanpada',
                    'Juinagar', 'Nerul', 'Seawoods', 'Belapur', 'Kharghar',
                    'Mansarovar', 'Khandeshwar', 'Panvel'
                ],
                'fare_zones': {
                    ('CSMT', 'Panvel'): {'2nd': 20, '1st': 100, 'AC': 110},
                    ('CSMT', 'Vashi'): {'2nd': 15, '1st': 70, 'AC': 80},
                    ('CSMT', 'Nerul'): {'2nd': 18, '1st': 85, 'AC': 95},
                    ('Kurla', 'Panvel'): {'2nd': 15, '1st': 75, 'AC': 85},
                    ('Kurla', 'Vashi'): {'2nd': 10, '1st': 50, 'AC': 60},
                    ('Vashi', 'Panvel'): {'2nd': 10, '1st': 35, 'AC': 45}
                }
            },
            # Default fare calculation based on distance zones
            'default_fares': {
                'short': {'2nd': 5, '1st': 25, 'AC': 35},    # 0-5 km
                'medium': {'2nd': 10, '1st': 50, 'AC': 70},   # 5-15 km  
                'long': {'2nd': 15, '1st': 75, 'AC': 85},     # 15-30 km
                'very_long': {'2nd': 20, '1st': 100, 'AC': 110}  # 30+ km
            }
        }
            
    def fetch_otp_stations(self):
        """Fetch all transit stops from OTP server"""
        try:
            url = f"{self.otp_base_url}/index/stops"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                stops_data = response.json()
                stations = []
                
                for stop in stops_data:
                    stations.append({
                        'name': stop.get('name', ''),
                        'lat': stop.get('lat', 0),
                        'lng': stop.get('lon', 0),  # OTP uses 'lon' not 'lng'
                        'type': 'TRANSIT_STOP',
                        'id': stop.get('id', '')
                    })
                
                return stations
            else:
                print(f"❌ OTP stops API returned status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to OTP server for stations")
        except Exception as e:
            print(f"❌ Error fetching stations from OTP: {e}")
            
        return None
    
    def get_mock_stations(self):
        """Mock Mumbai stations for demo"""
        return [
            {"name": "Churchgate", "lat": 18.9322, "lng": 72.8264, "type": "WR"},
            {"name": "Marine Lines", "lat": 18.9456, "lng": 72.8239, "type": "WR"},
            {"name": "Charni Road", "lat": 18.9539, "lng": 72.8200, "type": "WR"},
            {"name": "Grant Road", "lat": 18.9633, "lng": 72.8152, "type": "WR"},
            {"name": "Mumbai Central", "lat": 18.9686, "lng": 72.8181, "type": "WR"},
            {"name": "Mahalaxmi", "lat": 18.9827, "lng": 72.8186, "type": "WR"},
            {"name": "Lower Parel", "lat": 18.9969, "lng": 72.8331, "type": "WR"},
            {"name": "Elphinstone Road", "lat": 19.0041, "lng": 72.8339, "type": "WR"},
            {"name": "Dadar", "lat": 19.0178, "lng": 72.8478, "type": "WR"},
            {"name": "Matunga Road", "lat": 19.0270, "lng": 72.8489, "type": "WR"},
            {"name": "Mahim", "lat": 19.0411, "lng": 72.8411, "type": "WR"},
            {"name": "Bandra", "lat": 19.0544, "lng": 72.8406, "type": "WR"},
            {"name": "Khar Road", "lat": 19.0689, "lng": 72.8372, "type": "WR"},
            {"name": "Santacruz", "lat": 19.0822, "lng": 72.8386, "type": "WR"},
            {"name": "Vile Parle", "lat": 19.0989, "lng": 72.8469, "type": "WR"},
            {"name": "Andheri", "lat": 19.1197, "lng": 72.8469, "type": "WR"},
            # CR Line
            {"name": "CST", "lat": 18.9398, "lng": 72.8355, "type": "CR"},
            {"name": "Masjid", "lat": 18.9556, "lng": 72.8408, "type": "CR"},
            {"name": "Sandhurst Road", "lat": 18.9644, "lng": 72.8447, "type": "CR"},
            {"name": "King's Circle", "lat": 19.0270, "lng": 72.8578, "type": "CR"},
            {"name": "Kurla", "lat": 19.0692, "lng": 72.8789, "type": "CR"},
            {"name": "Ghatkopar", "lat": 19.0864, "lng": 72.9081, "type": "CR"},
            {"name": "Thane", "lat": 19.1972, "lng": 72.9636, "type": "CR"}
        ]
    
    def get_all_stations(self):
        """Get all stations for frontend dropdown"""
        if isinstance(self.stations, list):
            return self.stations
        else:
            # If stations.json has different structure, adapt accordingly
            return list(self.stations.values()) if isinstance(self.stations, dict) else []
    
    def get_routes(self, origin, destination, user_profile):
        """Get and optimize routes based on user profile"""
        try:
            print(f"🔍 Getting routes from {origin} to {destination}")
            
            # If origin/destination are strings, convert to coordinates
            origin_coords = self.get_station_coordinates(origin)
            destination_coords = self.get_station_coordinates(destination)
            
            if not origin_coords or not destination_coords:
                print("❌ Could not find coordinates for origin/destination")
                return self.get_mock_routes(origin, destination, user_profile)
            
            # Get multiple routes from OTP
            raw_routes = self.fetch_otp_routes(origin_coords, destination_coords)
            
            if not raw_routes:
                print("⚠️  No routes from OTP, using mock data")
                return self.get_mock_routes(origin, destination, user_profile)
            
            # Apply optimization logic
            optimized_routes = self.optimize_routes(raw_routes, user_profile)
            
            # If we have no real routes, supplement with mock routes
            if len(optimized_routes) < 1:
                print(f"🎭 No real routes found, adding mock routes")
                mock_routes = self.get_mock_routes(origin, destination, user_profile)
                
                # Add mock routes that are different from real ones
                for mock_route in mock_routes:
                    if len(optimized_routes) >= 5:
                        break
                    
                    # Check if this mock route is significantly different
                    is_different = True
                    for real_route in optimized_routes:
                        if abs(mock_route['duration'] - real_route['duration']) < 10:
                            is_different = False
                            break
                    
                    if is_different:
                        mock_route['route_id'] = len(optimized_routes) + 1
                        optimized_routes.append(mock_route)
                        print(f"✅ Added mock route: {mock_route['route_type']} - {mock_route['duration']}min")
            
            print(f"✅ Returning {len(optimized_routes)} total routes (real + mock)")
            return optimized_routes
            
        except Exception as e:
            print(f"❌ Error in get_routes: {e}")
            return self.get_mock_routes(origin, destination, user_profile)
    
    def get_station_coordinates(self, station_name):
        """Get coordinates for a station name with enhanced fuzzy matching"""
        if isinstance(station_name, dict):
            return station_name  # Already has coordinates
            
        print(f"🔍 Looking up coordinates for: '{station_name}'")
        
        # Normalize the search term
        search_term = station_name.lower().strip()
        
        # Search strategies
        exact_match = None
        best_partial_match = None
        word_matches = []
        
        for station in self.stations:
            if isinstance(station, dict):
                name = station.get('name', '').lower().strip()
                
                # 1. Exact match
                if name == search_term:
                    exact_match = station
                    break
                
                # 2. Partial matching (contains each other)
                if search_term in name or name in search_term:
                    if not best_partial_match or len(name) < len(best_partial_match.get('name', '')):
                        best_partial_match = station
                
                # 3. Word-based matching for complex names like "D.N.NAGAR, BARFIWALA VIDYALAYA"
                search_words = [w.strip() for w in search_term.replace(',', ' ').replace('.', ' ').split() if w.strip()]
                station_words = [w.strip() for w in name.replace(',', ' ').replace('.', ' ').split() if w.strip()]
                
                # Count matching words
                matching_words = 0
                for search_word in search_words:
                    for station_word in station_words:
                        if search_word in station_word or station_word in search_word:
                            matching_words += 1
                            break
                
                if matching_words > 0:
                    match_score = matching_words / len(search_words)
                    word_matches.append((station, match_score, matching_words))
        
        # Use the best match found
        found_station = None
        match_type = ""
        
        if exact_match:
            found_station = exact_match
            match_type = "exact"
        elif best_partial_match:
            found_station = best_partial_match
            match_type = "partial"
        elif word_matches:
            # Sort by match score, then by number of matching words
            word_matches.sort(key=lambda x: (x[1], x[2]), reverse=True)
            found_station = word_matches[0][0]
            match_type = f"word ({word_matches[0][1]:.2f} score)"
        
        if found_station:
            coords = {
                'lat': found_station['lat'], 
                'lng': found_station.get('lng') or found_station.get('lon')
            }
            print(f"✅ Found coordinates: {coords['lat']}, {coords['lng']} for '{found_station['name']}' (match: {match_type})")
            return coords
        
        # Fallback: Try to use known Mumbai area coordinates
        mumbai_areas = {
            'andheri': {'lat': 19.1136, 'lng': 72.8697},
            'bandra': {'lat': 19.0544, 'lng': 72.8406},
            'churchgate': {'lat': 18.9322, 'lng': 72.8264},
            'dadar': {'lat': 19.0178, 'lng': 72.8478},
            'mumbai central': {'lat': 18.9686, 'lng': 72.8181},
            'lower parel': {'lat': 18.9969, 'lng': 72.8331},
            'kurla': {'lat': 19.0692, 'lng': 72.8789},
            'ghatkopar': {'lat': 19.0864, 'lng': 72.9081},
            'thane': {'lat': 19.1972, 'lng': 72.9636},
            'navi mumbai': {'lat': 19.0330, 'lng': 73.0297}
        }
        
        # Check if station name contains known area
        search_lower = search_term.lower()
        for area, coords in mumbai_areas.items():
            if area in search_lower or any(word in area for word in search_lower.split()):
                print(f"✅ Using approximate coordinates for '{area}': {coords['lat']}, {coords['lng']}")
                return coords
        
        print(f"❌ Could not find coordinates for station: '{station_name}'")
        print(f"📝 Available stations sample: {[s.get('name', 'Unknown')[:40] for s in self.stations[:5] if isinstance(s, dict)]}")
        return None
    
    def fetch_otp_routes(self, origin, destination):
        """Fetch comprehensive routes mixing all transport modes for best optimization"""
        try:
            # Current time
            now = datetime.now()
            
            # Comprehensive mode combinations for different route types
            mode_combinations = [
                # Public transit combinations
                ('WALK,TRANSIT', 'all_transit'),
                ('WALK,BUS', 'bus_only'),
                ('WALK,RAIL', 'rail_only'),  
                ('WALK,SUBWAY', 'metro_only'),
                ('WALK,BUS,RAIL', 'bus_rail_mix'),
                ('WALK,BUS,SUBWAY', 'bus_metro_mix'),
                ('WALK,RAIL,SUBWAY', 'rail_metro_mix'),
                
                # Auto-rickshaw options
                ('CAR', 'auto_direct'),
                ('WALK,CAR', 'walk_auto_mix'),
                
                # Mixed multimodal (auto + transit)
                ('WALK,BUS,CAR', 'auto_bus_mix'),
                ('WALK,RAIL,CAR', 'auto_rail_mix'),
                
                # Walking options
                ('WALK', 'walk_only'),
            ]
            
            all_routes = []
            
            for modes, route_category in mode_combinations:
                # Different optimization targets
                optimization_variants = [
                    {'optimize': 'QUICK', 'transferPenalty': 300},     # Fastest
                    {'optimize': 'TRANSFERS', 'transferPenalty': 1800}, # Fewest transfers
                    {'optimize': 'WALKING', 'transferPenalty': 600},   # Balanced
                ]
                
                for variant in optimization_variants:
                    params = {
                        'fromPlace': f"{origin['lat']},{origin['lng']}",
                        'toPlace': f"{destination['lat']},{destination['lng']}",
                        'time': now.strftime('%H:%M'),
                        'date': now.strftime('%m-%d-%Y'),
                        'mode': modes,
                        'optimize': variant['optimize'],
                        'maxTransfers': 5,
                        'numItineraries': 2,
                        'arriveBy': 'false',
                        'walkReluctance': 2,
                        'transferPenalty': variant['transferPenalty'],
                        'waitReluctance': 1.5,
                        'walkSpeed': 1.3  # m/s - average walking speed
                    }
                    
                    print(f"🌐 Calling OTP: {modes} (optimize: {variant['optimize']})")
                    
                    try:
                        response = requests.get(self.otp_url, params=params, timeout=30)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if 'plan' in data and 'itineraries' in data['plan']:
                                routes = data['plan']['itineraries']
                                print(f"✅ Got {len(routes)} routes for {modes} ({variant['optimize']})")
                                
                                # Tag routes with their category and optimization
                                for route in routes:
                                    route['_category'] = route_category
                                    route['_optimization'] = variant['optimize']
                                    route['_mode_combo'] = modes
                                
                                all_routes.extend(routes)
                            else:
                                print(f"⚠️  No routes for {modes} ({variant['optimize']})")
                        else:
                            print(f"❌ OTP error {response.status_code} for {modes}")
                            
                    except requests.exceptions.Timeout:
                        print(f"⏰ Timeout for {modes} ({variant['optimize']})")
                        continue
                    except Exception as e:
                        print(f"❌ Error for {modes}: {e}")
                        continue
            
            if all_routes:
                # Advanced deduplication and categorization
                unique_routes = self.categorize_and_deduplicate_routes(all_routes)
                print(f"✅ Total categorized routes: {len(unique_routes)}")
                return unique_routes
            else:
                print("⚠️  No routes found, falling back to mock data")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching comprehensive routes: {e}")
            return []
    
    def categorize_and_deduplicate_routes(self, all_routes):
        """Categorize routes by fastest, cheapest, fewest transfers and remove duplicates. Filter out direct auto routes."""
        
        # First filter out direct auto-only and walk-only routes
        filtered_routes = []
        for route in all_routes:
            is_direct_only = self.is_direct_auto_route(route)  # Now filters both auto and walk
            if is_direct_only:
                print(f"🚫 Filtering out direct-only route: {route.get('duration', 0)}min, ₹{route.get('cost', 0)}")
            else:
                filtered_routes.append(route)
        
        print(f"✅ Route filtering: {len(all_routes)} → {len(filtered_routes)} routes")
        
        categorized = {
            'fastest': [],
            'cheapest': [],
            'fewest_transfers': [],
            'mixed': []
        }
        
        # Calculate metrics for filtered routes
        route_metrics = []
        for route in filtered_routes:
            duration = route.get('duration', 0) / 60  # minutes
            transfers = self.count_transfers(route)
            cost_info = self.estimate_cost(route)
            cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
            
            # Calculate composite scores
            route_metrics.append({
                'route': route,
                'duration': duration,
                'transfers': transfers,
                'cost': cost,
                'speed_score': 100 / max(duration, 1),  # Higher is faster
                'transfer_score': 100 / max(transfers + 1, 1),  # Higher is fewer transfers
                'cost_score': 100 / max(cost, 1)  # Higher is cheaper
            })
        
        # Sort by different criteria
        by_speed = sorted(route_metrics, key=lambda x: x['duration'])
        by_cost = sorted(route_metrics, key=lambda x: x['cost'])
        by_transfers = sorted(route_metrics, key=lambda x: x['transfers'])
        
        # Select best routes for each category
        unique_signatures = set()
        
        def add_unique_route(route_data, category):
            route = route_data['route']
            # Create signature to avoid duplicates
            signature = f"{int(route_data['duration']//5)}_{route_data['transfers']}_{int(route_data['cost']//10)}"
            
            if signature not in unique_signatures and len(categorized[category]) < 3:
                unique_signatures.add(signature)
                categorized[category].append(route)
                return True
            return False
        
        # Add fastest routes
        for route_data in by_speed[:5]:
            add_unique_route(route_data, 'fastest')
        
        # Add cheapest routes  
        for route_data in by_cost[:5]:
            add_unique_route(route_data, 'cheapest')
        
        # Add fewest transfer routes
        for route_data in by_transfers[:5]:
            add_unique_route(route_data, 'fewest_transfers')
        
        # Add some mixed/balanced routes
        balanced = sorted(route_metrics, key=lambda x: -(x['speed_score'] + x['transfer_score'] + x['cost_score']))
        for route_data in balanced[:3]:
            if len(categorized['mixed']) < 2:
                add_unique_route(route_data, 'mixed')
        
        # Flatten to single list with category tags
        final_routes = []
        for category, routes in categorized.items():
            for route in routes:
                route['_route_category'] = category
                final_routes.append(route)
        
        return final_routes[:10]  # Return top 10 diverse routes
    
    def is_direct_auto_route(self, route):
        """Check if this is a direct auto-only or walk-only route (not multimodal) - filter both"""
        legs = route.get('legs', [])
        
        # Count different transport modes (looking for CAR since conversion happens later)
        car_legs = [leg for leg in legs if leg.get('mode') == 'CAR']
        transit_legs = [leg for leg in legs if leg.get('mode') in ['BUS', 'RAIL', 'SUBWAY']]
        walk_legs = [leg for leg in legs if leg.get('mode') == 'WALK']
        
        print(f"🔍 Route check: {len(car_legs)} car, {len(transit_legs)} transit, {len(walk_legs)} walk legs")
        
        # Filter out direct walk routes (walk-only with no other transport)
        if len(walk_legs) > 0 and len(transit_legs) == 0 and len(car_legs) == 0:
            walk_duration = sum(leg.get('duration', 0) for leg in walk_legs)
            # Convert seconds to minutes if needed (OTP returns duration in seconds)
            if walk_duration > 1000:  # Likely in seconds
                walk_duration = walk_duration / 60
            if walk_duration > 60:  # Filter out very long walking routes (>60 minutes)
                print(f"🚫 Marking as direct walk route (walk: {walk_duration:.1f}min)")
                return True
        
        # Filter out direct car/auto routes (car-only with no public transit)
        if len(car_legs) > 0 and len(transit_legs) == 0:
            # Calculate total non-walk duration
            non_walk_duration = sum(leg.get('duration', 0) for leg in legs if leg.get('mode') != 'WALK')
            car_duration = sum(leg.get('duration', 0) for leg in car_legs)
            
            # Convert seconds to minutes if needed (OTP returns duration in seconds)
            if car_duration > 1000:  # Likely in seconds
                car_duration = car_duration / 60
                non_walk_duration = non_walk_duration / 60
            
            print(f"🚗 Car duration: {car_duration:.1f} min, Non-walk duration: {non_walk_duration:.1f} min")
            
            # If car is the dominant mode (more than 60% of non-walk time) and longer than 20 minutes
            if car_duration > 20 and (car_duration / max(non_walk_duration, 1)) > 0.6:
                print(f"🚫 Marking as direct auto route (car: {car_duration:.1f}min / total non-walk: {non_walk_duration:.1f}min)")
                return True
                
        return False
    
    def optimize_routes(self, routes, user_profile):
        """Optimize routes and categorize by Fastest, Cheapest, and Fewest Transfers"""
        if not routes:
            return []
        
        print(f"🔍 Optimizing {len(routes)} routes with categorical approach")
        
        # Calculate comprehensive metrics for all routes
        route_analysis = []
        
        for route in routes:
            duration_minutes = route['duration'] / 60
            transfers = self.count_transfers(route)
            cost_info = self.estimate_cost(route)
            cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
            walk_time = route.get('walkTime', 0) / 60
            
            # Get route category if available
            category = route.get('_route_category', 'mixed')
            
            route_data = {
                'raw_route': route,
                'duration': duration_minutes,
                'transfers': transfers,
                'cost': cost,
                'walk_time': walk_time,
                'category': category,
                'score': self.calculate_score(route, user_profile),
                'eco_score': self.calculate_eco_score(route)
            }
            
            route_analysis.append(route_data)
            print(f"📊 Route: {duration_minutes:.1f}min, {transfers} transfers, ₹{cost} ({category})")
        
        # Categorize routes by primary criteria
        categorized_routes = {
            'fastest': [],
            'cheapest': [],
            'fewest_transfers': []
        }
        
        # Sort by each criteria
        by_speed = sorted(route_analysis, key=lambda x: x['duration'])
        by_cost = sorted(route_analysis, key=lambda x: x['cost'])
        by_transfers = sorted(route_analysis, key=lambda x: (x['transfers'], x['duration']))
        
        print("🚀 FASTEST ROUTES:")
        for i, route_data in enumerate(by_speed[:2]):
            if route_data not in categorized_routes['fastest']:
                categorized_routes['fastest'].append(route_data)
                print(f"  {i+1}. {route_data['duration']:.1f}min, {route_data['transfers']} transfers, ₹{route_data['cost']}")
        
        print("💰 CHEAPEST ROUTES:")
        for i, route_data in enumerate(by_cost[:2]):
            if route_data not in categorized_routes['cheapest']:
                categorized_routes['cheapest'].append(route_data)
                print(f"  {i+1}. ₹{route_data['cost']}, {route_data['duration']:.1f}min, {route_data['transfers']} transfers")
        
        print("🔄 FEWEST TRANSFERS:")
        for i, route_data in enumerate(by_transfers[:2]):
            if route_data not in categorized_routes['fewest_transfers']:
                categorized_routes['fewest_transfers'].append(route_data)
                print(f"  {i+1}. {route_data['transfers']} transfers, {route_data['duration']:.1f}min, ₹{route_data['cost']}")
        
        # Convert back to frontend format with proper categorization
        final_routes = []
        route_id = 1
        
        # Add fastest routes
        for route_data in categorized_routes['fastest']:
            formatted_route = self.format_route_for_frontend(route_data, route_id, "Fastest")
            final_routes.append(formatted_route)
            route_id += 1
        
        # Add cheapest routes (if different from fastest)
        for route_data in categorized_routes['cheapest']:
            if not any(abs(r['duration'] - route_data['duration']) < 2 for r in final_routes):
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Cheapest")
                final_routes.append(formatted_route)
                route_id += 1
        
        # Add fewest transfer routes (if different from others)
        for route_data in categorized_routes['fewest_transfers']:
            if not any(abs(r['duration'] - route_data['duration']) < 2 for r in final_routes):
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Direct" if route_data['transfers'] == 0 else "Best")
                final_routes.append(formatted_route)
                route_id += 1
        
        # Ensure we have at least 3 routes by adding balanced options
        if len(final_routes) < 3:
            remaining_routes = [r for r in route_analysis if not any(abs(fr['duration'] - r['duration']) < 3 for fr in final_routes)]
            balanced_routes = sorted(remaining_routes, key=lambda x: -(x['score']))
            
            for route_data in balanced_routes[:3-len(final_routes)]:
                formatted_route = self.format_route_for_frontend(route_data, route_id, "Good")
                final_routes.append(formatted_route)
                route_id += 1
        
        print(f"✅ Returning {len(final_routes)} categorized routes")
        return final_routes[:5]  # Maximum 5 routes
    
    def format_route_for_frontend(self, route_data, route_id, route_type):
        """Format route data for frontend consumption with detailed fare information"""
        raw_route = route_data['raw_route']
        cost_info = self.estimate_cost(raw_route)
        
        return {
            'route_id': route_id,
            'duration': int(route_data['duration']),
            'transfers': route_data['transfers'],
            'score': round(route_data['score'], 2),
            'cost': cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info,
            'fare_breakdown': cost_info.get('breakdown', []) if isinstance(cost_info, dict) else [],
            'eco_score': round(route_data['eco_score'], 1),
            'route_type': route_type,
            'legs': self.format_legs(raw_route.get('legs', [])),
            'start_time': raw_route.get('startTime', 0),
            'end_time': raw_route.get('endTime', 0),
            'walkTime': route_data['walk_time'],
            'transitTime': raw_route.get('transitTime', 0) / 60,
            'waitingTime': raw_route.get('waitingTime', 0) / 60,
            'raw_route': raw_route
        }
    
    def count_transfers(self, route):
        """Count number of transfers in a route including auto-rickshaw"""
        transit_legs = 0
        for leg in route.get('legs', []):
            mode = leg.get('mode')
            if mode in ['BUS', 'RAIL', 'SUBWAY', 'TRAM', 'CAR']:  # CAR = auto-rickshaw
                transit_legs += 1
        return max(0, transit_legs - 1)  # First boarding is not a transfer
    
    def calculate_score(self, route, profile):
        """Calculate route score based on user profile"""
        transfer_weight = profile.get('transfer_preference', 0.4)
        time_weight = profile.get('time_preference', 0.3)
        cost_weight = profile.get('cost_preference', 0.2)
        eco_weight = profile.get('eco_preference', 0.1)
        
        # Normalize scores (0-10 scale)
        transfers = self.count_transfers(route)
        duration_minutes = route['duration'] / 60
        
        transfer_score = max(0, 10 - transfers * 3)  # Fewer transfers = higher score
        time_score = max(0, 10 - duration_minutes / 10)  # Faster = higher score
        cost_info = self.estimate_cost(route)
        cost = cost_info['total_cost'] if isinstance(cost_info, dict) else cost_info
        cost_score = max(0, 10 - cost / 10)  # Cheaper = higher score
        eco_score = self.calculate_eco_score(route)
        
        total_score = (
            transfer_score * transfer_weight +
            time_score * time_weight +
            cost_score * cost_weight +
            eco_score * eco_weight
        )
        
        return total_score
    
    def calculate_train_fare(self, from_station, to_station, distance_km=0):
        """Calculate accurate Mumbai train fare between stations with class options"""
        
        # Clean and normalize station names
        from_station = self.normalize_station_name(from_station)
        to_station = self.normalize_station_name(to_station)
        
        print(f"🚂 Calculating train fare: {from_station} → {to_station} ({distance_km:.1f}km)")
        
        # Try to find exact fare from our fare table
        for line, line_data in self.train_fares.items():
            if line == 'default_fares':
                continue
                
            fare_zones = line_data.get('fare_zones', {})
            
            # Check direct route
            direct_key = (from_station, to_station)
            reverse_key = (to_station, from_station)
            
            if direct_key in fare_zones:
                fares = fare_zones[direct_key]
                print(f"✅ Found direct fare on {line}: 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
                return fares
            elif reverse_key in fare_zones:
                fares = fare_zones[reverse_key] 
                print(f"✅ Found reverse fare on {line}: 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
                return fares
        
        # If no exact match, use distance-based calculation
        if distance_km > 0:
            if distance_km <= 5:
                zone = 'short'
            elif distance_km <= 15:
                zone = 'medium'
            elif distance_km <= 30:
                zone = 'long'
            else:
                zone = 'very_long'
                
            fares = self.train_fares['default_fares'][zone]
            print(f"✅ Using distance-based fare ({zone}): 2nd=₹{fares['2nd']}, 1st=₹{fares['1st']}, AC=₹{fares['AC']}")
            return fares
        
        # Ultimate fallback
        default_fare = {'2nd': 10, '1st': 50, 'AC': 70}
        print(f"⚠️  Using default train fare: 2nd=₹{default_fare['2nd']}, 1st=₹{default_fare['1st']}, AC=₹{default_fare['AC']}")
        return default_fare
    
    def normalize_station_name(self, station_name):
        """Normalize station names for fare lookup"""
        if not station_name:
            return ""
            
        # Convert to standard format
        name = station_name.strip().upper()
        
        # Common name mappings
        name_mappings = {
            'CST': 'CSMT',
            'CSMT': 'CSMT',  # Keep CSMT as-is
            'CHHATRAPATI SHIVAJI TERMINUS': 'CSMT', 
            'CHHATRAPATI SHIVAJI MAHARAJ TERMINUS': 'CSMT',
            'VT': 'CSMT',
            'VICTORIA TERMINUS': 'CSMT',
            'MUMBAI CENTRAL': 'Mumbai Central',
            'BCT': 'Mumbai Central',
            'BOMBAY CENTRAL': 'Mumbai Central',
            'CHURCHGATE': 'Churchgate',
            'DADAR': 'Dadar',
            'ANDHERI': 'Andheri',
            'BORIVALI': 'Borivali',
            'VIRAR': 'Virar',
            'KURLA': 'Kurla',
            'THANE': 'Thane',
            'KALYAN': 'Kalyan',
            'PANVEL': 'Panvel',
            'VASHI': 'Vashi',
            'NERUL': 'Nerul'
        }
        
        return name_mappings.get(name, station_name.title())
    
    def estimate_cost(self, route):
        """Estimate route cost in INR with accurate Mumbai transport pricing and class options (2025)"""
        total_cost = 0
        fare_breakdown = []
        
        for leg in route.get('legs', []):
            mode = leg.get('mode', '')
            distance = leg.get('distance', 0) / 1000  # Convert to km
            from_name = self.extract_place_name(leg.get('from', {}))
            to_name = self.extract_place_name(leg.get('to', {}))
            
            leg_cost = 0
            fare_details = {}
            
            if mode == 'BUS':
                # BEST bus fare: ₹8-₹25 based on distance
                if distance <= 3:
                    leg_cost = 8  # Short distance
                elif distance <= 10:
                    leg_cost = 15  # Medium distance
                else:
                    leg_cost = 25  # Long distance
                    
                fare_details = {
                    'mode': 'BUS',
                    'operator': 'BEST',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fare': leg_cost,
                    'route_number': leg.get('tripShortName', '').replace('-UP', '').replace('-DN', '')
                }
                    
            elif mode == 'RAIL':
                # Mumbai Local Train: Use accurate fare table
                train_fares = self.calculate_train_fare(from_name, to_name, distance)
                leg_cost = train_fares['2nd']  # Default to 2nd class for cost calculation
                
                # Determine line based on route information
                route_info = leg.get('routeLongName', '')
                line = 'WR' if 'western' in route_info.lower() else 'CR' if 'central' in route_info.lower() else 'HR' if 'harbour' in route_info.lower() else 'LOCAL'
                
                fare_details = {
                    'mode': 'RAIL',
                    'operator': 'Indian Railways',
                    'line': line,
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fares': {
                        '2nd_class': train_fares['2nd'],
                        '1st_class': train_fares['1st'], 
                        'ac_local': train_fares['AC']
                    },
                    'default_fare': train_fares['2nd']
                }
                    
            elif mode == 'SUBWAY':
                # Mumbai Metro: ₹10-₹50 based on distance and specific route patterns
                if distance <= 3:
                    leg_cost = 10  # Short metro ride (1-3 stations)
                elif distance <= 6:
                    leg_cost = 20  # Medium metro ride
                elif distance <= 12:
                    leg_cost = 40  # Long metro ride (like Ghatkopar to D.N.Nagar = 9.5km)
                else:
                    leg_cost = 50  # Very long metro ride (end-to-end Blue Line)
                    
                fare_details = {
                    'mode': 'METRO',
                    'operator': 'Mumbai Metro',
                    'line': 'Blue Line (ML-1)',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'fare': leg_cost
                }
                    
            elif mode == 'TRAM':
                leg_cost = 5   # Heritage tram (rare)
                fare_details = {
                    'mode': 'TRAM',
                    'operator': 'BEST',
                    'from': from_name,
                    'to': to_name,
                    'fare': leg_cost
                }
                
            elif mode in ['CAR', 'AUTO']:  # Auto-rickshaw
                # Mumbai auto fare 2025: ₹28 base + ₹18/km (with traffic surcharge)
                base_fare = 28
                distance_fare = distance * 18
                # Add waiting time surcharge for longer trips
                if distance > 3:
                    distance_fare += 10  # Traffic/waiting surcharge
                leg_cost = base_fare + distance_fare
                
                fare_details = {
                    'mode': 'AUTO',
                    'operator': 'Auto Rickshaw',
                    'from': from_name,
                    'to': to_name,
                    'distance_km': round(distance, 1),
                    'base_fare': base_fare,
                    'distance_fare': round(distance_fare),
                    'total_fare': round(leg_cost)
                }
            
            # WALK mode has no cost
            if leg_cost > 0:
                total_cost += leg_cost
                fare_breakdown.append(fare_details)
        
        return {
            'total_cost': max(5, int(total_cost)),  # Minimum ₹5, rounded to integer
            'breakdown': fare_breakdown
        }
    
    def calculate_eco_score(self, route):
        """Calculate eco-friendliness score (0-10) based on transport modes and emissions"""
        total_distance = 0
        eco_points = 0
        
        # Calculate points based on transport modes used
        for leg in route.get('legs', []):
            distance = leg.get('distance', 0) / 1000  # Convert to km
            mode = leg.get('mode', 'WALK')
            total_distance += distance
            
            # Eco points per km based on transport mode
            if mode == 'WALK':
                eco_points += distance * 10  # Walking is best (10 points/km)
            elif mode in ['RAIL', 'SUBWAY']:
                eco_points += distance * 8   # Public transit is great (8 points/km)
            elif mode == 'BUS':
                eco_points += distance * 5   # Bus is average (5 points/km)
            elif mode == 'TRAM':
                eco_points += distance * 9   # Tram is excellent (9 points/km)
            elif mode in ['CAR', 'AUTO']:
                eco_points += distance * 2   # Auto/car is poor (2 points/km)
            else:
                eco_points += distance * 5   # Unknown mode gets neutral score
        
        if total_distance == 0:
            return 5.0
        
        # Calculate final score (0-10 scale)
        # Perfect score (10) = average 8+ points per km (mostly public transport + walking)
        # Good score (7-9) = average 6-8 points per km (mix of public transport)
        # Average score (5-7) = average 4-6 points per km (some private transport)
        # Poor score (1-4) = average <4 points per km (mostly private transport)
        
        avg_points_per_km = eco_points / total_distance
        eco_score = min(10, max(1, avg_points_per_km * 1.25))  # Scale to 0-10
        
        return round(eco_score, 1)
    
    def get_route_type(self, route, profile, route_index=0):
        """Determine route type label based on route characteristics"""
        transfers = self.count_transfers(route)
        duration = route['duration'] / 60  # minutes
        walk_time = route.get('walkTime', 0) / 60  # minutes
        
        # Check if it's an auto-rickshaw route (CAR mode converted to AUTO)
        legs = route.get('legs', [])
        has_auto = any(leg.get('mode') == 'CAR' for leg in legs)
        if has_auto:
            return "Direct" if transfers == 0 else "Premium"
        
        # Check for specific transit modes
        has_rail = any(leg.get('mode') == 'RAIL' for leg in legs)
        has_bus = any(leg.get('mode') == 'BUS' for leg in legs)
        has_subway = any(leg.get('mode') == 'SUBWAY' for leg in legs)
        
        # First route is usually "Best" unless it's clearly something else
        if route_index == 0 and not has_auto:
            return "Best"
        
        # Direct routes (no transfers)
        if transfers == 0:
            if has_rail:
                return "Direct"
            elif has_bus:
                return "Direct"
            else:
                return "Direct"
        
        # Fast routes (short duration)
        if duration <= 35:
            return "Fastest"
        
        # Eco-friendly routes (more walking)
        if walk_time > duration * 0.25:  # 25%+ walking
            return "Eco"
        
        # Rail-based routes
        if has_rail and not has_bus:
            return "Express" if transfers <= 1 else "Rail"
        
        # Bus-only routes
        if has_bus and not has_rail:
            return "Budget" if transfers <= 1 else "Economy"
        
        # Mixed mode routes
        if has_rail and has_bus:
            return "Comfort" if transfers <= 2 else "Mixed"
        
        # Metro routes
        if has_subway:
            return "Metro"
        
        # Default classification based on transfers
        if transfers == 1:
            return "Good"
        elif transfers == 2:
            return "Standard"
        else:
            return "Alternative"
    
    def format_legs(self, legs):
        """Format route legs for frontend display with enhanced OTP data extraction"""
        formatted = []
        for leg in legs:
            # Extract mode information and convert CAR to AUTO for better UX
            mode = leg.get('mode', 'WALK')
            if mode == 'CAR':
                mode = 'AUTO'  # Convert car to auto-rickshaw for Indian context
            
            # Extract route information (for transit legs) with proper bus/train numbers
            route_info = ''
            route_number = ''
            if mode not in ['WALK', 'AUTO']:
                # Try to get route number from multiple fields in priority order
                # For bus routes, extract from tripShortName or headsign
                trip_short = leg.get('tripShortName', '')
                headsign = leg.get('headsign', '')
                route_short = leg.get('routeShortName', '')
                
                if mode == 'BUS':
                    # Extract bus number from tripShortName (like "56-UP", "2LTD-UP", "181-UP")
                    if trip_short and trip_short != 'BEST':
                        # Remove direction suffixes
                        route_number = trip_short.replace('-UP', '').replace('-DN', '').replace('2:', '').strip()
                    elif headsign and headsign not in ['BEST Bus', 'BEST']:
                        route_number = headsign.replace('-UP', '').replace('-DN', '').strip()
                    elif route_short and route_short not in ['BEST', 'BEST Bus']:
                        route_number = route_short
                        
                    # Clean up route number
                    if route_number and route_number != 'BEST':
                        route_description = f"BEST {route_number}"
                    else:
                        route_number = 'BEST'
                        route_description = 'BEST Bus'
                        
                elif mode == 'RAIL':
                    # For trains, get the line name and train info
                    route_description = leg.get('routeLongName', 'Local Train')
                    if trip_short:
                        # Extract train info (like "Virar - Churchgate", "AAR-DAH-235")
                        if ' - ' in trip_short:
                            route_number = trip_short.split(' - ')[0]
                        else:
                            route_number = trip_short.replace('2:', '')
                    elif route_short:
                        route_number = route_short
                    else:
                        route_number = 'LOCAL'
                        
                elif mode == 'SUBWAY':
                    # For metro, get the line name and number
                    route_description = leg.get('routeLongName', 'Metro')
                    if route_short:
                        route_number = route_short
                    elif trip_short:
                        route_number = trip_short.replace('2:', '')
                    else:
                        route_number = 'ML-1'
                
                # Combine route number and description for display
                if mode == 'BUS':
                    route_info = route_description  # Already formatted as "BEST {number}"
                elif mode == 'RAIL':
                    if route_number and route_number != 'LOCAL':
                        route_info = f"{route_number} - {route_description}" if route_description != route_number else route_number
                    else:
                        route_info = route_description
                elif mode == 'SUBWAY':
                    if route_number and route_description:
                        route_info = f"{route_number} - {route_description}" if route_description != route_number else route_number
                    else:
                        route_info = route_description or 'Metro'
                        
                # Fallback to generic names if nothing found
                if not route_info:
                    if mode == 'BUS':
                        route_info = 'BEST Bus'
                        route_number = 'BEST'
                    elif mode == 'RAIL':
                        route_info = 'Local Train'
                        route_number = 'LOCAL'
                    elif mode == 'SUBWAY':
                        route_info = 'Metro'
                        route_number = 'ML-1'
                    else:
                        route_info = mode
                        route_number = mode
            elif mode == 'AUTO':
                route_info = 'Auto Rickshaw'
                route_number = 'AUTO'
            
            # Extract timing information with fallback calculation
            duration_seconds = leg.get('duration', 0)
            start_time = leg.get('startTime', 0)
            end_time = leg.get('endTime', 0)
            
            # Calculate duration from timestamps if duration is 0 or missing
            if duration_seconds == 0 and start_time and end_time:
                duration_seconds = (end_time - start_time) / 1000  # Convert milliseconds to seconds
                print(f"🔧 Calculated duration from timestamps: {duration_seconds}s for {mode}")
            
            duration_minutes = int(duration_seconds / 60) if duration_seconds else 0
            
            # For transit legs, ensure minimum realistic duration based on distance
            if mode in ['BUS', 'RAIL', 'SUBWAY'] and duration_minutes < 1:
                distance_km = leg.get('distance', 0) / 1000
                if distance_km > 0.5:  # Only for distances > 500m
                    # Estimate minimum duration based on mode and distance
                    if mode == 'BUS':
                        # Mumbai bus average speed: 15-20 km/h in traffic
                        estimated_minutes = max(2, int(distance_km * 4))  # ~15 km/h average
                    elif mode == 'SUBWAY':
                        # Mumbai metro average speed: 35-40 km/h including stops
                        estimated_minutes = max(1, int(distance_km * 2))  # ~30 km/h average
                    elif mode == 'RAIL':
                        # Mumbai local train average speed: 40-50 km/h including stops
                        estimated_minutes = max(2, int(distance_km * 1.5))  # ~40 km/h average
                    
                    if estimated_minutes > duration_minutes:
                        duration_minutes = estimated_minutes
                        print(f"🔧 Adjusted {mode} duration to {duration_minutes}min based on {distance_km:.1f}km distance")
            
            # Extract location information
            from_place = leg.get('from', {})
            to_place = leg.get('to', {})
            
            # Get proper station/stop names with better cleaning
            from_name = self.extract_place_name(from_place)
            to_name = self.extract_place_name(to_place)
            
            # Extract distance
            distance = int(leg.get('distance', 0))
            
            formatted_leg = {
                'mode': mode,
                'route': route_info,
                'route_number': route_number,  # Add specific route number
                'duration': duration_minutes,
                'distance': distance,
                'from_name': from_name,
                'to_name': to_name,
                'start_time': start_time,
                'end_time': end_time,
                'departureTime': self.format_timestamp(start_time) if start_time else None,
                'arrivalTime': self.format_timestamp(end_time) if end_time else None
            }
            
            # Add transit-specific information with enhanced route details
            if mode not in ['WALK', 'AUTO']:
                # Add route-specific details
                formatted_leg.update({
                    'routeLongName': leg.get('routeLongName', ''),
                    'routeShortName': leg.get('routeShortName', ''),
                    'routeId': leg.get('routeId', ''),
                    'headsign': leg.get('headsign', ''),
                })
                
                # Add trip information if available
                if 'trip' in leg:
                    trip_info = leg['trip']
                    formatted_leg.update({
                        'trip_headsign': trip_info.get('tripHeadsign', ''),
                        'trip_id': trip_info.get('tripId', ''),
                        'trip_short_name': trip_info.get('tripShortName', ''),
                        'block_id': trip_info.get('blockId', '')
                    })
                
                # Add agency information
                if 'agencyName' in leg:
                    formatted_leg['agency'] = leg['agencyName']
            
            formatted.append(formatted_leg)
            
        return formatted
    
    def extract_place_name(self, place):
        """Extract a readable place name from OTP place object with better cleaning"""
        if not place:
            return 'Unknown'
        
        # Try different name fields in order of preference
        name = (place.get('name') or 
                place.get('stopName') or 
                place.get('stationName') or 
                place.get('vertexType', ''))
        
        # Clean up the name for better readability
        if name:
            # Remove coordinate suffixes like "::1234,5678"
            if '::' in name:
                name = name.split('::')[0]
            
            # Remove parenthetical coordinates
            if name.endswith(')') and '(' in name:
                paren_pos = name.rfind('(')
                potential_coords = name[paren_pos+1:-1]
                # Check if it looks like coordinates (numbers, commas, dots)
                if all(c.isdigit() or c in '.,- ' for c in potential_coords):
                    name = name[:paren_pos].strip()
            
            # Clean up common OTP artifacts
            name = name.replace('_', ' ')
            name = ' '.join(word.capitalize() for word in name.split())
            
            # Handle common Mumbai station name patterns
            if 'STATION' in name.upper():
                name = name.replace('STATION', 'Station')
            if 'ROAD' in name.upper():
                name = name.replace('ROAD', 'Road')
            if 'DEPOT' in name.upper():
                name = name.replace('DEPOT', 'Depot')
                
            return name
        
        # Fallback to coordinates if no name available
        lat = place.get('lat', 0)
        lon = place.get('lon', 0)
        return f"Location ({lat:.4f}, {lon:.4f})"
    
    def format_timestamp(self, timestamp):
        """Format Unix timestamp to readable time"""
        if not timestamp:
            return None
        
        try:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp / 1000)  # OTP uses milliseconds
            return dt.strftime('%H:%M')
        except:
            return None
    
    def get_mock_routes(self, origin, destination, user_profile):
        """Generate diverse mock routes demonstrating multimodal transport combinations"""
        print("🎭 Generating multimodal mock routes (no direct auto)")
        
        routes = [
            # Walk to nearest station + Train - Cheapest option
            {
                'route_id': 1,
                'duration': 45,
                'transfers': 1,
                'score': 8.5,
                'cost': 10,  # Just train fare (₹10 for medium distance)
                'eco_score': 8.8,
                'route_type': 'Cheapest',
                'fare_breakdown': [
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways',
                        'line': 'WR',
                        'from': 'Nearest Railway Station',
                        'to': 'Destination Station',
                        'distance_km': 6.2,
                        'fares': {
                            '2nd_class': 10,
                            '1st_class': 35,
                            'ac_local': 45
                        },
                        'default_fare': 10
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 12, 'from_name': origin, 'to_name': 'Nearest Railway Station', 'distance': 800, 'route': '', 'route_number': ''},
                    {'mode': 'RAIL', 'route': 'WR - Western Line', 'route_number': 'WR', 'duration': 28, 'from_name': 'Nearest Railway Station', 'to_name': 'Destination Station', 'distance': 6200},
                    {'mode': 'WALK', 'duration': 5, 'from_name': 'Destination Station', 'to_name': destination, 'distance': 300, 'route': '', 'route_number': ''}
                ]
            },
            
            # Auto to station + Train - Balanced option
            {
                'route_id': 2,
                'duration': 35,
                'transfers': 1,
                'score': 8.2,
                'cost': 56,  # ₹46 auto (₹28 base + ₹18/km for 1.2km) + ₹10 train
                'eco_score': 7.5,
                'route_type': 'Fastest',
                'fare_breakdown': [
                    {
                        'mode': 'AUTO',
                        'operator': 'Auto Rickshaw',
                        'from': 'Pickup Point',
                        'to': 'Major Railway Station',
                        'distance_km': 1.2,
                        'base_fare': 28,
                        'distance_fare': 22,
                        'total_fare': 50
                    },
                    {
                        'mode': 'RAIL',
                        'operator': 'Indian Railways', 
                        'line': 'HR',
                        'from': 'Major Railway Station',
                        'to': 'Destination Station',
                        'distance_km': 5.8,
                        'fares': {
                            '2nd_class': 10,
                            '1st_class': 50,
                            'ac_local': 60
                        },
                        'default_fare': 10
                    }
                ],
                'legs': [
                    {'mode': 'WALK', 'duration': 3, 'from_name': origin, 'to_name': 'Pickup Point', 'distance': 150, 'route': '', 'route_number': ''},
                    {'mode': 'AUTO', 'route': 'Auto Rickshaw', 'route_number': 'AUTO', 'duration': 8, 'from_name': 'Pickup Point', 'to_name': 'Major Railway Station', 'distance': 1200},
                    {'mode': 'RAIL', 'route': 'HR - Harbour Line', 'route_number': 'HR', 'duration': 20, 'from_name': 'Major Railway Station', 'to_name': 'Destination Station', 'distance': 5800},
                    {'mode': 'WALK', 'duration': 4, 'from_name': 'Destination Station', 'to_name': destination, 'distance': 250, 'route': '', 'route_number': ''}
                ]
            },
            
            # Walk + Bus + Metro - Mixed transport
            {
                'route_id': 3,
                'duration': 48,
                'transfers': 2,
                'score': 7.8,
                'cost': 55,  # ₹15 bus (medium distance) + ₹40 metro (long distance like Ghatkopar-D.N.Nagar)
                'eco_score': 8.2,
                'route_type': 'Mixed',
                'legs': [
                    {'mode': 'WALK', 'duration': 8, 'from_name': origin, 'to_name': 'Bus Stop A', 'distance': 400, 'route': '', 'route_number': ''},
                    {'mode': 'BUS', 'route': 'BEST 201', 'route_number': '201', 'duration': 22, 'from_name': 'Bus Stop A', 'to_name': 'Metro Station', 'distance': 3200},
                    {'mode': 'SUBWAY', 'route': 'ML-1 - Blue Line', 'route_number': 'ML-1', 'duration': 15, 'from_name': 'Metro Station', 'to_name': 'Destination Metro', 'distance': 4200},
                    {'mode': 'WALK', 'duration': 3, 'from_name': 'Destination Metro', 'to_name': destination, 'distance': 200, 'route': '', 'route_number': ''}
                ]
            },
            
            # Auto to Bus Terminal + Bus - Alternative
            {
                'route_id': 4,
                'duration': 42,
                'transfers': 1,
                'score': 7.5,
                'cost': 71,  # ₹56 auto (₹28 base + ₹28 for 1.8km) + ₹15 bus
                'eco_score': 6.8,
                'route_type': 'Alternative',
                'legs': [
                    {'mode': 'WALK', 'duration': 4, 'from_name': origin, 'to_name': 'Auto Stand', 'distance': 200, 'route': '', 'route_number': ''},
                    {'mode': 'AUTO', 'route': 'Auto Rickshaw', 'route_number': 'AUTO', 'duration': 12, 'from_name': 'Auto Stand', 'to_name': 'Bus Terminal', 'distance': 1800},
                    {'mode': 'BUS', 'route': 'BEST 340', 'route_number': '340', 'duration': 23, 'from_name': 'Bus Terminal', 'to_name': 'Near Destination', 'distance': 4500},
                    {'mode': 'WALK', 'duration': 3, 'from_name': 'Near Destination', 'to_name': destination, 'distance': 180, 'route': '', 'route_number': ''}
                ]
            }
        ]
        
        # Filter based on user profile
        max_transfers = user_profile.get('max_transfers', 3)
        filtered_routes = [r for r in routes if r['transfers'] <= max_transfers]
        
        return filtered_routes[:3]