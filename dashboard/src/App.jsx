
import { useEffect, useState } from "react";
import { Circle, MapContainer, Marker, Popup, TileLayer, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const EIDW = {
  code: "EIDW",
  name: "Dublin Airport",
  lat: 53.4213,
  lon: -6.2701
};

const OPEN_SKY_URL = "/api/opensky/tar90?limit=250";
const TRANSCRIPTS_URL = "/api/transcripts?limit=40";

const FLIGHT_ICON = L.divIcon({
  className: "flight-icon-wrap",
  html: '<div class="flight-icon">✈</div>',
  iconSize: [30, 30],
  iconAnchor: [15, 15]
});

function getDistanceKm(lat1, lon1, lat2, lon2) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const earthRadiusKm = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return earthRadiusKm * c;
}

function formatAltitude(meters, onGround) {
  if (onGround) return "0 ft";
  if (meters === null || meters === undefined) return "0 ft";
  return `${(meters * 3.28084).toFixed(0)} ft`;
}

function formatSpeed(ms, kts) {
  if (kts !== null && kts !== undefined) return `${kts.toFixed(0)} kt`;
  if (!ms) return "0 kt";
  return `${(ms * 1.94384).toFixed(0)} kt`;
}

function toFlightObjects(flights = []) {
  return flights
    .map((f) => ({
      id: f.icao24,
      callsign: (f.callsign || "").trim() || "UNK",
      lat: f.latitude,
      lon: f.longitude,
      onGround: !!f.on_ground,
      velocity: f.speed_mps,
      speedKts: f.speed_kts,
      baroAltitude: f.baro_altitude_m,
      geoAltitude: f.geo_altitude_m
    }))
    .filter((f) => typeof f.lat === "number" && typeof f.lon === "number");
}

export default function App() {
  const [flights, setFlights] = useState([]);
  const [mapStatus, setMapStatus] = useState("SYSTEM READY");
  const [transcriptLines, setTranscriptLines] = useState([]);

  useEffect(() => {
    const fetchFlights = async () => {
      try {
        const response = await fetch(OPEN_SKY_URL);
        const data = await response.json();
        setFlights(toFlightObjects(data.flights || []));
        setMapStatus(`TRAFFIC: ${data.flights?.length || 0} ACFT`);
      } catch (e) { setMapStatus("OFFLINE"); }
    };
    fetchFlights();
    const timer = setInterval(fetchFlights, 15000); //refresh
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchTranscripts = async () => {
      try {
        const response = await fetch(`${TRANSCRIPTS_URL}&t=${Date.now()}`);
        const data = await response.json();
        setTranscriptLines(Array.isArray(data.entries) ? data.entries : []);
      } catch (e) { console.error("Radio Error"); }
    };
    fetchTranscripts();
    const timer = setInterval(fetchTranscripts, 5000); 
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <h1>✈ Sky <span className="highlight">Transcript</span></h1>
          <p>DUBLIN INTERNATIONAL RADAR</p>
        </div>
        <div className="status-container">
          <span className="live-indicator">● LIVE FEED</span>
          <div className="status-badge">{mapStatus}</div>
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="map-area">
          <MapContainer 
            center={[EIDW.lat, EIDW.lon]} 
            zoom={10} 
            className="map-canvas" 
            attributionControl={false}
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />

            <Circle
              center={[EIDW.lat, EIDW.lon]}
              radius={18000}
              pathOptions={{ color: "#00aaff", fillColor: "#00aaff", fillOpacity: 0.1, weight: 3, dashArray: "8, 12" }}
            />

            {flights.map((f) => ( //pop-up
              <Marker key={f.id} position={[f.lat, f.lon]} icon={FLIGHT_ICON}>
                <Tooltip permanent direction="top" offset={[0, -15]} className="plane-tooltip">
                  {f.callsign}
                </Tooltip>
                <Popup className="custom-popup">
                  <div className="popup-header">
                    <h3>{f.callsign}</h3>
                    <code>{f.id.toUpperCase()}</code>
                  </div>
                  <div className="popup-body">
                    <p>Altitude: <strong>{formatAltitude(f.geoAltitude ?? f.baroAltitude, f.onGround)}</strong></p>
                    <p>Speed: <strong>{formatSpeed(f.velocity, f.speedKts)}</strong></p>
                    <p>Latitude: <strong>{f.lat.toFixed(4)}</strong></p>
                    <p>Longitude: <strong>{f.lon.toFixed(4)}</strong></p>
                    <p>Distance: <strong>{getDistanceKm(EIDW.lat, EIDW.lon, f.lat, f.lon).toFixed(1)} km</strong></p>
                    <p className={f.onGround ? "status-ground" : "status-air"}>{f.onGround ? "ON GROUND" : "AIRBORNE"}</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </section>

        <section className="log-area">
          <div className="log-header">ATC RADIO TRANSCRIPTION</div>
          <div className="log-content">
            {transcriptLines.length === 0 ? (
              <div className="empty-log">Scanning frequencies...</div>
            ) : (
              transcriptLines.slice().reverse().map((line, i) => (
                <div key={i} className="log-entry">
                  <span className="log-time">[{line.timestamp}]</span>
                  <span className="log-text">{line.text}</span>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
