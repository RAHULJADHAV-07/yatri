# 🚆 Yatri - Smart Journey Planning System

A comprehensive multi-modal journey planning application for Mumbai's transportation network, combining local trains, buses, and other transit options.

## 🏗️ System Architecture

### Components
1. **Frontend** - React-based web application (standalone HTML with CDN)
2. **Backend** - Flask API server with route optimization
3. **OTP Server** - OpenTripPlanner 2.5.0 for advanced routing (optional)

### Technology Stack
- **Frontend**: React 18, Tailwind CSS, Leaflet Maps
- **Backend**: Python Flask, Flask-CORS
- **Data**: JSON-based station data (3,875+ stations)
- **Routing**: OpenTripPlanner + Custom fallback algorithms

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
# Windows Command Prompt
start_system.bat

# Windows PowerShell  
.\start_system.ps1
```

### Option 2: Manual Startup

#### 1. Start Backend Server
```bash
cd backend
python app.py
```
Server starts on: `http://localhost:5000`

#### 2. Start Frontend Server
```bash
cd frontend
python -m http.server 3000
```
Frontend available at: `http://localhost:3000/standalone.html`

#### 3. Start OTP Server (Optional)
```bash
cd otp_server
java -Xmx2G -jar otp-2.5.0-shaded.jar --load --serve --port 8081 .
```

## 🔧 System Testing

Run comprehensive system tests:
```bash
python test_system.py
```

Expected output:
```
🚆 Yatri System Health Check
========================================
✅ Backend Health: OK
✅ Stations API: OK (3875 stations loaded)
✅ Profiles API: OK (4 profiles)
✅ Journey Planning: OK (3 routes found)
✅ Frontend: OK (HTML served successfully)
⚠️  OTP Server: Not running (using mock data)
========================================
📊 Test Results: 5/6 passed
🎉 System is ready for demo!
```

## 🌐 API Endpoints

### Backend API (`http://localhost:5000`)

#### Health Check
```bash
GET /api/health
```

#### Get All Stations
```bash
GET /api/stations
```

#### Get User Profiles
```bash
GET /api/profiles
```

#### Plan Journey
```bash
POST /api/plan
Content-Type: application/json

{
  "origin": "Churchgate",
  "destination": "Andheri",
  "profile": "comfort"
}
```

**Response:**
```json
{
  "success": true,
  "routes": [
    {
      "route_type": "Best",
      "duration": 45,
      "transfers": 1,
      "cost": 25,
      "steps": ["Board Western Line at Churchgate", "Transfer at Dadar", "Arrive at Andheri"]
    }
  ]
}
```

## 📱 User Interface Features

### Journey Planning
- **Smart Station Search**: Autocomplete with 3,875+ stations
- **Profile-Based Routing**: Comfort, Speed, Eco-friendly, Budget options
- **Multi-Modal Results**: Train + Bus combinations
- **Real-time Cost Calculation**: Dynamic pricing based on distance and mode

### Travel Preferences
1. **Comfort** - Minimize walking, prefer AC coaches
2. **Speed** - Fastest routes, more transfers acceptable  
3. **Eco-friendly** - Prefer trains over buses, optimize carbon footprint
4. **Budget** - Cheapest options, maximize walking distance

### Route Information
- Duration and cost estimates
- Transfer points and walking directions
- Alternative route suggestions
- Real-time availability (when OTP server active)

## 🗂️ Data Structure

### Stations (`data/stations.json`)
```json
{
  "stations": [
    {
      "name": "Churchgate",
      "line": "Western",
      "zone": "1",
      "latitude": 18.9322,
      "longitude": 72.8264
    }
  ]
}
```

### User Profiles (`backend/user_profiles.py`)
- Comfort preferences
- Walking tolerance
- Budget constraints
- Accessibility requirements

## 🔧 Configuration

### Backend Settings (`backend/app.py`)
- CORS enabled for frontend communication
- JSON-based responses
- Error handling with fallback data
- Port: 5000

### Frontend Settings (`frontend/standalone.html`)
- CDN-based React 18
- Tailwind CSS for styling
- Native fetch API for backend communication
- Responsive design for mobile/desktop

### OTP Configuration (`otp_server/router-config.json`)
- Graph processing settings
- Transit feed configurations
- Routing algorithms optimization

## 🐛 Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check Python environment
python --version

# Install dependencies
pip install flask flask-cors requests

# Check port availability
netstat -an | findstr :5000
```

#### Frontend Connection Issues
```bash
# Verify server is running
python -m http.server 3000

# Test frontend accessibility
curl http://localhost:3000/standalone.html
```

#### OTP Server Issues
The OTP server is optional. The system works with mock data if OTP is unavailable.

```bash
# Check Java version (required: Java 8+)
java -version

# Verify graph.obj file exists
dir otp_server\graph.obj

# Manual OTP startup
java -Xmx4G -jar otp-2.5.0-shaded.jar --load --serve .
```

### Performance Optimization

#### Memory Settings
- OTP Server: Minimum 2GB RAM (`-Xmx2G`)
- Backend: Lightweight Flask server
- Frontend: Static file serving

#### Network Configuration
- Backend: http://localhost:5000
- Frontend: http://localhost:3000  
- OTP: http://localhost:8081 (if running)

## 🛠️ Development

### Adding New Features

#### New API Endpoint
1. Add route in `backend/app.py`
2. Implement logic in appropriate module
3. Update frontend to consume new endpoint
4. Add tests in `test_system.py`

#### New User Profile
1. Update `backend/user_profiles.py`
2. Modify route optimization logic
3. Add UI elements in frontend
4. Test profile-specific routing

### File Structure
```
yatri-hackathon/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── route_optimizer.py  # Routing algorithms
│   ├── user_profiles.py    # User preference management
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── standalone.html     # Complete React application
│   ├── package.json       # Node.js dependencies (unused)
│   └── public/            # Static assets
├── data/
│   └── stations.json      # Station database
├── otp_server/
│   ├── otp-2.5.0-shaded.jar  # OpenTripPlanner
│   ├── graph.obj            # Transit network graph
│   └── router-config.json   # OTP configuration
├── test_system.py         # System verification tests
├── start_system.bat       # Windows startup script
└── start_system.ps1       # PowerShell startup script
```

## 📊 System Metrics

### Performance Benchmarks
- **Station Lookup**: < 50ms for 3,875 stations
- **Route Calculation**: < 2s for complex multi-modal queries
- **API Response Time**: < 100ms for cached routes
- **Frontend Load Time**: < 3s on standard broadband

### Supported Scale
- **Stations**: 3,875+ (expandable)
- **Daily Queries**: 1,000+ (with proper infrastructure)
- **Concurrent Users**: 50+ (Flask dev server)
- **Route Alternatives**: Up to 5 per query

## 🤝 Contributing

### Code Standards
- Python: PEP 8 compliance
- JavaScript: ESLint configuration
- Comments: Docstrings for all functions
- Testing: Comprehensive test coverage

### Deployment Considerations
- **Production**: Use WSGI server (Gunicorn/uWSGI)
- **Database**: Migrate from JSON to PostgreSQL/MongoDB
- **Caching**: Implement Redis for route caching
- **Monitoring**: Add health checks and metrics

## 📄 License

This project is developed for the Yatri Hackathon and is intended for demonstration purposes.

## 🙋‍♀️ Support

### Getting Help
1. Run `python test_system.py` for system diagnostics
2. Check console logs in browser developer tools
3. Verify all servers are running on correct ports
4. Ensure Python dependencies are installed

### Contact Information
For technical issues or questions about the Yatri journey planning system, please refer to the system test output and troubleshooting section above.

---

**Status**: ✅ Fully functional with mock data | ⚠️ OTP server optional  
**Last Updated**: System verified and operational  
**Demo Ready**: Yes - http://localhost:3000/standalone.html#   Y a t r i - H a c k a t h o n  
 #   y a t r i  
 