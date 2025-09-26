import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet with Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapModal = ({ route, isOpen, onClose, origin, destination }) => {
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const routeLayer = useRef(null);

  useEffect(() => {
    if (isOpen && route && mapRef.current && !leafletMap.current) {
      initializeLeafletMap();
    }

    return () => {
      if (leafletMap.current) {
        leafletMap.current.remove();
        leafletMap.current = null;
      }
    };
  }, [isOpen]);

  useEffect(() => {
    if (isOpen && route && leafletMap.current) {
      updateMapWithRoute(route);
    }
  }, [isOpen, route]);

  const initializeLeafletMap = () => {
    if (!mapRef.current) return;

    // Mumbai coordinates (center of the city)
    const mumbaiCenter = [19.0760, 72.8777];
    
    // Create the map
    leafletMap.current = L.map(mapRef.current, {
      center: mumbaiCenter,
      zoom: 11,
      zoomControl: true,
      scrollWheelZoom: true,
    });

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(leafletMap.current);
  };

  const updateMapWithRoute = (route) => {
    if (!leafletMap.current || !route) return;

    // Clear existing route layer
    if (routeLayer.current) {
      leafletMap.current.removeLayer(routeLayer.current);
    }

    // Create new layer group for route
    routeLayer.current = L.layerGroup().addTo(leafletMap.current);

    if (route.legs && route.legs.length > 0) {
      // Use real route coordinates from the legs data
      const routeCoords = extractRealRouteCoordinates(route);
      
      if (routeCoords.length > 0) {
        // Create route polyline with different colors for different modes
        const segments = createRouteSegments(route.legs, routeCoords);
        
        segments.forEach((segment, index) => {
          const color = getTransportModeColor(segment.mode);
          const routeLine = L.polyline(segment.coords, {
            color: color,
            weight: 6,
            opacity: 0.8,
            dashArray: segment.mode === 'WALK' ? '5, 10' : '0'
          }).addTo(routeLayer.current);

          // Add popup to each segment
          routeLine.bindPopup(`
            <strong>${segment.mode === 'WALK' ? '🚶 Walking' : 
                     segment.mode === 'BUS' ? '🚌 Bus' : 
                     segment.mode === 'RAIL' ? '🚊 Train' : 
                     segment.mode === 'SUBWAY' ? '🚇 Metro' : 
                     segment.mode === 'AUTO' ? '🛺 Auto' : segment.mode}</strong><br/>
            ${segment.route ? `Route: ${segment.route}<br/>` : ''}
            Duration: ${segment.duration} min<br/>
            Distance: ${segment.distance}m
          `);
        });

        // Add start marker (green)
        const startIcon = L.divIcon({
          html: '<div class="route-marker start">🚀</div>',
          className: 'custom-marker',
          iconSize: [40, 40],
          iconAnchor: [20, 20]
        });
        
        L.marker(routeCoords[0], { icon: startIcon })
          .addTo(routeLayer.current)
          .bindPopup(`<strong>Start: ${origin}</strong><br/>Your journey begins here`);

        // Add end marker (red)
        const endIcon = L.divIcon({
          html: '<div class="route-marker end">🎯</div>',
          className: 'custom-marker',
          iconSize: [40, 40],
          iconAnchor: [20, 20]
        });
        
        L.marker(routeCoords[routeCoords.length - 1], { icon: endIcon })
          .addTo(routeLayer.current)
          .bindPopup(`<strong>Destination: ${destination}</strong><br/>Your journey ends here`);

        // Add transfer points based on actual leg transitions
        let coordIndex = 0;
        route.legs.forEach((leg, legIndex) => {
          if (legIndex > 0 && legIndex < route.legs.length - 1 && leg.mode !== 'WALK') {
            const transferIcon = L.divIcon({
              html: '<div class="route-marker transfer">🔄</div>',
              className: 'custom-marker',
              iconSize: [30, 30],
              iconAnchor: [15, 15]
            });
            
            if (routeCoords[coordIndex]) {
              L.marker(routeCoords[coordIndex], { icon: transferIcon })
                .addTo(routeLayer.current)
                .bindPopup(`<strong>Transfer Point</strong><br/>
                           From: ${leg.from_name}<br/>
                           To: ${leg.to_name}<br/>
                           Change to: ${leg.mode}`);
            }
          }
          coordIndex += Math.ceil(leg.duration / 5); // Approximate coordinate spacing
        });

        // Fit map to show entire route
        if (routeCoords.length > 1) {
          const bounds = L.latLngBounds(routeCoords);
          leafletMap.current.fitBounds(bounds, { padding: [20, 20] });
        }
      }
    }
  };

  const extractRealRouteCoordinates = (route) => {
    // Try to extract coordinates from the raw route data if available
    if (route.raw_route && route.raw_route.legs) {
      const coords = [];
      route.raw_route.legs.forEach(leg => {
        if (leg.from && leg.from.lat && leg.from.lon) {
          coords.push([leg.from.lat, leg.from.lon]);
        }
        if (leg.to && leg.to.lat && leg.to.lon) {
          coords.push([leg.to.lat, leg.to.lon]);
        }
      });
      if (coords.length > 0) return coords;
    }

    // Fallback: Generate coordinates based on Mumbai station locations
    return generateMumbaiRouteCoordinates(route, origin, destination);
  };

  const generateMumbaiRouteCoordinates = (route, origin, destination) => {
    // Known Mumbai station coordinates
    const mumbaiStations = {
      'CHURCHGATE': [18.9322, 72.8264],
      'MARINE LINES': [18.9456, 72.8239],
      'CHARNI ROAD': [18.9539, 72.8200],
      'GRANT ROAD': [18.9633, 72.8152],
      'MUMBAI CENTRAL': [18.9686, 72.8181],
      'MAHALAXMI': [18.9827, 72.8186],
      'LOWER PAREL': [18.9969, 72.8331],
      'ELPHINSTONE ROAD': [19.0041, 72.8339],
      'DADAR': [19.0178, 72.8478],
      'MATUNGA ROAD': [19.0270, 72.8489],
      'MAHIM': [19.0411, 72.8411],
      'BANDRA': [19.0544, 72.8406],
      'KHAR ROAD': [19.0689, 72.8372],
      'SANTACRUZ': [19.0822, 72.8386],
      'VILE PARLE': [19.0989, 72.8469],
      'ANDHERI': [19.1197, 72.8469],
      'JOGESHWARI': [19.1347, 72.8492],
      'RAM MANDIR': [19.1481, 72.8492],
      'GOREGAON': [19.1647, 72.8500],
      'MALAD': [19.1864, 72.8486],
      'KANDIVALI': [19.2039, 72.8500],
      'BORIVALI': [19.2306, 72.8567],
      // Central Line
      'CST': [18.9398, 72.8355],
      'MASJID': [18.9556, 72.8408],
      'SANDHURST ROAD': [18.9644, 72.8447],
      'BYCULLA': [18.9761, 72.8314],
      'CHINCHPOKLI': [18.9889, 72.8283],
      'CURREY ROAD': [19.0022, 72.8431],
      'PAREL': [19.0069, 72.8331],
      'KINGS CIRCLE': [19.0270, 72.8578],
      'WADALA': [19.0169, 72.8578],
      'KURLA': [19.0692, 72.8789],
      'VIDYAVIHAR': [19.0825, 72.8897],
      'GHATKOPAR': [19.0864, 72.9081],
      'VIKHROLI': [19.1072, 72.9264],
      'KANJURMARG': [19.1289, 72.9394],
      'BHANDUP': [19.1447, 72.9394],
      'NAHUR': [19.1547, 72.9547],
      'MULUND': [19.1681, 72.9561],
      'THANE': [19.1972, 72.9636],
      // Popular locations
      'D.N.NAGAR': [19.1744, 72.8350],
      'BARFIWALA': [19.1744, 72.8350], // Same as D.N.Nagar
      'PRIYDARSHINI': [19.0544, 72.8406], // Near Bandra
      'NAGPADA': [18.9686, 72.8181], // Near Mumbai Central
      'VERSOVA': [19.1281, 72.8097],
      'GHATKOPAR': [19.0864, 72.9081]
    };

    // Find coordinates for origin and destination
    const originCoords = findStationCoords(origin, mumbaiStations);
    const destCoords = findStationCoords(destination, mumbaiStations);

    if (!originCoords || !destCoords) {
      // Fallback to Mumbai center if stations not found
      return [[19.0760, 72.8777], [19.0760, 72.8777]];
    }

    // Generate intermediate points based on route legs
    const coords = [originCoords];
    
    if (route.legs && route.legs.length > 1) {
      const totalLegs = route.legs.length;
      for (let i = 1; i < totalLegs; i++) {
        const leg = route.legs[i];
        
        // Try to find coordinates for leg stations
        if (leg.from_name && leg.to_name) {
          const legFromCoords = findStationCoords(leg.from_name, mumbaiStations);
          const legToCoords = findStationCoords(leg.to_name, mumbaiStations);
          
          if (legFromCoords) coords.push(legFromCoords);
          if (legToCoords && i === totalLegs - 1) coords.push(legToCoords);
        } else {
          // Interpolate between origin and destination
          const ratio = i / totalLegs;
          const lat = originCoords[0] + (destCoords[0] - originCoords[0]) * ratio;
          const lng = originCoords[1] + (destCoords[1] - originCoords[1]) * ratio;
          coords.push([lat, lng]);
        }
      }
    }
    
    // Ensure destination is the last point
    if (coords[coords.length - 1] !== destCoords) {
      coords.push(destCoords);
    }

    return coords;
  };

  const findStationCoords = (stationName, stations) => {
    if (!stationName) return null;
    
    const cleanName = stationName.toUpperCase().trim();
    
    // Direct match
    if (stations[cleanName]) return stations[cleanName];
    
    // Partial match
    for (const [name, coords] of Object.entries(stations)) {
      if (name.includes(cleanName) || cleanName.includes(name)) {
        return coords;
      }
    }
    
    return null;
  };

  const createRouteSegments = (legs, routeCoords) => {
    const segments = [];
    let coordIndex = 0;
    
    legs.forEach((leg, index) => {
      const segmentCoords = [];
      const pointsPerLeg = Math.max(2, Math.ceil(routeCoords.length / legs.length));
      
      for (let i = 0; i < pointsPerLeg && coordIndex < routeCoords.length; i++) {
        segmentCoords.push(routeCoords[coordIndex]);
        coordIndex++;
      }
      
      if (segmentCoords.length > 1) {
        segments.push({
          coords: segmentCoords,
          mode: leg.mode,
          route: leg.route,
          duration: leg.duration,
          distance: leg.distance
        });
      }
    });
    
    return segments;
  };

  const getTransportModeColor = (mode) => {
    const colors = {
      'WALK': '#10b981',     // Green
      'BUS': '#f59e0b',      // Orange  
      'RAIL': '#3b82f6',     // Blue
      'SUBWAY': '#8b5cf6',   // Purple
      'AUTO': '#ef4444',     // Red
      'CAR': '#ef4444'       // Red
    };
    return colors[mode] || '#6b7280'; // Gray fallback
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-2 sm:p-4 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-2xl w-full max-w-7xl h-[95vh] sm:h-[90vh] flex flex-col overflow-hidden animate-slideUp">
        {/* Enhanced Modal Header */}
        <div className="relative p-3 sm:p-6 bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 text-white">
          <div className="absolute inset-0 bg-black bg-opacity-10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 sm:space-x-4">
                <div className="p-2 sm:p-3 bg-white bg-opacity-20 rounded-xl backdrop-blur-sm">
                  <span className="text-lg sm:text-2xl">🗺️</span>
                </div>
                <div>
                  <h2 className="text-lg sm:text-2xl font-bold flex flex-col sm:flex-row sm:items-center">
                    Route Map
                    <span className="mt-1 sm:ml-3 sm:mt-0 px-2 sm:px-3 py-1 bg-white bg-opacity-20 rounded-full text-xs sm:text-sm font-medium backdrop-blur-sm">
                      {route?.route_type}
                    </span>
                  </h2>
                  <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 mt-2 text-blue-100 space-y-1 sm:space-y-0">
                    <div className="flex items-center space-x-1">
                      <span className="text-sm">📍</span>
                      <span className="text-xs sm:text-sm font-medium truncate">{origin}</span>
                    </div>
                    <div className="text-blue-200">→</div>
                    <div className="flex items-center space-x-1">
                      <span className="text-sm">🎯</span>
                      <span className="text-sm font-medium">{destination}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <div className="text-xl font-bold">{route?.duration}</div>
                    <div className="text-xs text-blue-200">minutes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold">₹{route?.cost}</div>
                    <div className="text-xs text-blue-200">total cost</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold">{route?.transfers}</div>
                    <div className="text-xs text-blue-200">transfers</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xl font-bold text-green-300">{route?.eco_score}/10</div>
                    <div className="text-xs text-blue-200">eco score</div>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-xl transition-all duration-200 text-white hover:text-blue-100 flex-shrink-0"
                  title="Close map"
                >
                  <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="flex-1 relative">
          <div ref={mapRef} className="w-full h-full"></div>
          
          {/* Enhanced Map Legend */}
          <div className="absolute bottom-3 sm:bottom-6 left-3 sm:left-6 bg-white bg-opacity-95 backdrop-blur-md rounded-xl sm:rounded-2xl p-3 sm:p-4 shadow-xl border border-gray-200 z-10 min-w-60 sm:min-w-64 max-w-[90vw] sm:max-w-none">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-base sm:text-lg font-bold text-gray-800 flex items-center">
                <span className="mr-2">🧭</span>
                Legend
              </h4>
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            </div>
            <div className="space-y-3">
              {/* Location Markers */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Locations</div>
                <div className="grid grid-cols-1 gap-2">
                  <div className="flex items-center justify-between p-2 bg-green-50 rounded-lg">
                    <div className="flex items-center">
                      <span className="mr-3 text-lg">🚀</span>
                      <span className="text-sm font-medium text-gray-800">Start Point</span>
                    </div>
                    <span className="text-xs text-green-600 font-medium">{origin}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-red-50 rounded-lg">
                    <div className="flex items-center">
                      <span className="mr-3 text-lg">🎯</span>
                      <span className="text-sm font-medium text-gray-800">Destination</span>
                    </div>
                    <span className="text-xs text-red-600 font-medium">{destination}</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-orange-50 rounded-lg">
                    <div className="flex items-center">
                      <span className="mr-3 text-lg">🔄</span>
                      <span className="text-sm font-medium text-gray-800">Transfer</span>
                    </div>
                    <span className="text-xs text-orange-600 font-medium">Change Mode</span>
                  </div>
                </div>
              </div>
              
              {/* Transport Modes */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Transport Modes</div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center p-2 bg-gray-50 rounded-lg">
                    <div className="w-4 h-2 bg-green-500 rounded-sm mr-2" style={{borderStyle: 'dashed', borderWidth: '1px'}}></div>
                    <span className="text-xs font-medium">Walking</span>
                  </div>
                  <div className="flex items-center p-2 bg-gray-50 rounded-lg">
                    <div className="w-4 h-2 bg-orange-500 rounded-sm mr-2"></div>
                    <span className="text-xs font-medium">Bus</span>
                  </div>
                  <div className="flex items-center p-2 bg-gray-50 rounded-lg">
                    <div className="w-4 h-2 bg-blue-500 rounded-sm mr-2"></div>
                    <span className="text-xs font-medium">Train</span>
                  </div>
                  <div className="flex items-center p-2 bg-gray-50 rounded-lg">
                    <div className="w-4 h-2 bg-purple-500 rounded-sm mr-2"></div>
                    <span className="text-xs font-medium">Metro</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Route Summary */}
          <div className="absolute top-3 sm:top-6 right-3 sm:right-6 bg-white bg-opacity-95 backdrop-blur-md rounded-xl sm:rounded-2xl p-3 sm:p-4 shadow-xl border border-gray-200 z-10 min-w-72 sm:min-w-80 max-w-[90vw] sm:max-w-none">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-bold text-gray-800 flex items-center">
                <span className="mr-2">📊</span>
                Route Details
              </h4>
              <div className="px-3 py-1 bg-gradient-to-r from-green-500 to-blue-500 text-white text-xs font-bold rounded-full">
                LIVE
              </div>
            </div>
            
            {/* Route Metrics */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-3 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">{route?.duration}</div>
                    <div className="text-xs text-blue-500 font-medium">Minutes</div>
                  </div>
                  <div className="text-blue-400">⏱️</div>
                </div>
              </div>
              <div className="bg-gradient-to-r from-green-50 to-green-100 p-3 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-green-600">₹{route?.cost}</div>
                    <div className="text-xs text-green-500 font-medium">Total Cost</div>
                  </div>
                  <div className="text-green-400">💰</div>
                </div>
              </div>
              <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-3 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-orange-600">{route?.transfers}</div>
                    <div className="text-xs text-orange-500 font-medium">Transfers</div>
                  </div>
                  <div className="text-orange-400">🔄</div>
                </div>
              </div>
              <div className="bg-gradient-to-r from-emerald-50 to-emerald-100 p-3 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-2xl font-bold text-emerald-600">{route?.eco_score}/10</div>
                    <div className="text-xs text-emerald-500 font-medium">Eco Score</div>
                  </div>
                  <div className="text-emerald-400">🌱</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Click on route segments for more details
            </div>
            <button
              onClick={onClose}
              className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Close Map
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapModal;