import React, { useState } from 'react';
import RouteDetailModal from './RouteDetailModal';
import MapModal from './MapModal';

const RouteResults = ({ routes, selectedRoute, onRouteSelect, loading, error, origin, destination }) => {
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [mapModalOpen, setMapModalOpen] = useState(false);
  const [modalRoute, setModalRoute] = useState(null);
  
  const handleRouteClick = (route) => {
    onRouteSelect(route);
  };

  const handleDetailClick = (route, event) => {
    event.stopPropagation(); // Prevent route selection
    setModalRoute(route);
    setDetailModalOpen(true);
  };

  const handleMapClick = (route, event) => {
    event.stopPropagation(); // Prevent route selection
    onRouteSelect(route); // Select the route first
    setModalRoute(route);
    setMapModalOpen(true);
  };
  
  const getModeIcon = (mode) => {
    const icons = {
      'WALK': '🚶',
      'BUS': '🚌',
      'RAIL': '🚂',
      'SUBWAY': '🚇',
      'TRAM': '🚋',
      'AUTO': '🛺'
    };
    return icons[mode] || '🚌';
  };

  const getRouteTypeColor = (type) => {
    const colors = {
      'Best': 'bg-green-100 text-green-800',
      'Fastest': 'bg-blue-100 text-blue-800',
      'Budget': 'bg-yellow-100 text-yellow-800',
      'Eco': 'bg-emerald-100 text-emerald-800',
      'Direct': 'bg-purple-100 text-purple-800',
      'Good': 'bg-gray-100 text-gray-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-center py-8">
          <div className="spinner mr-3"></div>
          <span className="text-gray-600">Finding best routes...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center py-8">
          <div className="text-red-500 text-2xl mb-2">⚠️</div>
          <h3 className="text-lg font-medium text-gray-800 mb-2">Unable to find routes</h3>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  if (routes.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="text-center py-8">
          <div className="text-gray-400 text-2xl mb-2">🗺️</div>
          <h3 className="text-lg font-medium text-gray-800 mb-2">Ready to plan</h3>
          <p className="text-sm text-gray-600">Select origin and destination to see route options</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-3 sm:p-6">
      <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3 sm:mb-4 flex items-center">
        <span className="mr-2">📍</span>
        Route Options ({routes.length})
      </h3>
      
      <div className="space-y-3">
        {routes.map((route) => (
          <div
            key={route.route_id}
            className={`route-card p-3 sm:p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedRoute?.route_id === route.route_id
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
            onClick={() => handleRouteClick(route)}
          >
            {/* Route Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 space-y-2 sm:space-y-0">
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 text-xs font-medium rounded ${getRouteTypeColor(route.route_type)}`}>
                  {route.route_type}
                </span>
                <div className="text-sm font-semibold text-gray-800">
                  {route.duration} min
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-800">₹{route.cost}</div>
                  <div className="text-xs text-gray-500">Score: {route.score}/10</div>
                </div>
                <button
                  onClick={(e) => handleMapClick(route, e)}
                  className="bg-green-500 hover:bg-green-600 text-white px-2 sm:px-3 py-1 rounded text-xs font-medium transition-colors flex items-center space-x-1"
                  title="Show route on map"
                >
                  <span>🗺️</span>
                  <span className="hidden sm:inline">Map</span>
                </button>
                <button
                  onClick={(e) => handleDetailClick(route, e)}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-2 sm:px-3 py-1 rounded text-xs font-medium transition-colors"
                  title="View detailed route information"
                >
                  <span className="hidden sm:inline">Details</span>
                  <span className="sm:hidden">ℹ️</span>
                </button>
              </div>
            </div>

            {/* Route Details */}
            <div className="space-y-2">
              {/* Transfers and Eco */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between text-sm space-y-1 sm:space-y-0">
                <div className="flex items-center text-gray-600">
                  <span className="mr-1">🔄</span>
                  {route.transfers} transfer{route.transfers !== 1 ? 's' : ''}
                </div>
                <div className="flex items-center text-gray-600">
                  <span className="mr-1">🌱</span>
                  Eco: {route.eco_score}/10
                </div>
              </div>

              {/* Route Steps */}
              <div className="flex flex-wrap items-center gap-1 text-xs">
                {route.legs && route.legs.slice(0, 4).map((leg, index) => (
                  <React.Fragment key={index}>
                    <div className="flex items-center bg-gray-100 rounded px-2 py-1">
                      <span className="mr-1">{getModeIcon(leg.mode)}</span>
                      <span className="text-gray-700">
                        {leg.mode === 'WALK' ? `${leg.duration}m` : leg.route || leg.mode}
                      </span>
                    </div>
                    {index < Math.min(route.legs.length - 1, 3) && (
                      <span className="text-gray-400">→</span>
                    )}
                  </React.Fragment>
                ))}
                {route.legs && route.legs.length > 4 && (
                  <span className="text-gray-400">...</span>
                )}
              </div>

              {/* Last Mile Options */}
              {route.last_mile && route.last_mile.length > 0 && (
                <div className="pt-2 border-t border-gray-100">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">Last-mile options:</span>
                    <div className="flex space-x-1">
                      {route.last_mile.slice(0, 3).map((option, index) => (
                        <button
                          key={index}
                          className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded transition-colors"
                          title={`${option.name}: ₹${option.cost}, ${option.time} min`}
                        >
                          {option.icon} ₹{option.cost}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Route Comparison */}
      {routes.length > 1 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <div className="flex justify-between">
              <span>Fastest route:</span>
              <span>{Math.min(...routes.map(r => r.duration))} min</span>
            </div>
            <div className="flex justify-between">
              <span>Cheapest route:</span>
              <span>₹{Math.min(...routes.map(r => r.cost))}</span>
            </div>
            <div className="flex justify-between">
              <span>Fewest transfers:</span>
              <span>{Math.min(...routes.map(r => r.transfers))}</span>
            </div>
          </div>
        </div>
      )}

      {/* Route Detail Modal */}
      <RouteDetailModal
        route={modalRoute}
        isOpen={detailModalOpen}
        onClose={() => {
          setDetailModalOpen(false);
          setModalRoute(null);
        }}
        origin={origin}
        destination={destination}
      />

      {/* Map Modal */}
      <MapModal
        route={modalRoute}
        isOpen={mapModalOpen}
        onClose={() => {
          setMapModalOpen(false);
          setModalRoute(null);
        }}
        origin={origin}
        destination={destination}
      />
    </div>
  );
};

export default RouteResults;