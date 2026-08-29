import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { floats, profiles } from "../data/mockData";
import {
    MapContainer,
    TileLayer,
    Polyline,
    CircleMarker,
    Popup,
  } from "react-leaflet";

function FloatDetails() {
  const { id } = useParams();

  const float = floats.find((item) => item.id === id);
  const profile = profiles[id];
  const trajectory = [

    [8.2, 58.5],

    [10.4, 61.8],

    [11.6, 63.9],

    [12.45, 65.32],

  ];

  if (!float) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="page-content">
          <h1>Float not found</h1>
        </main>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content float-details-page">
        <div className="float-details-header">
          <div>
            <span className="active-badge">● {float.status}</span>
            <h1>Float {float.id}</h1>
          </div>

          <div className="header-actions">
            <button>Save</button>
            <button>Share</button>
          </div>
        </div>

        <section className="float-summary-grid">
          <div className="summary-card">
            <span>CURRENT LOCATION</span>
            <strong>
              {float.latitude}°N, {float.longitude}°E
            </strong>
          </div>

          <div className="summary-card">
            <span>MAX DEPTH</span>
            <strong>{float.maxDepth} m</strong>
          </div>

          <div className="summary-card">
            <span>LATEST PROFILE</span>
            <strong>25 Aug 2026</strong>
          </div>

          <div className="summary-card">
            <span>TOTAL PROFILES</span>
            <strong>156</strong>
          </div>
        </section>

        <section className="float-main-grid">
          <div className="trajectory-card">
            <h3>Trajectory Map</h3>

            <MapContainer
  center={[10.5, 62]}
  zoom={4}
  className="details-map"
>
  <TileLayer
    attribution="&copy; OpenStreetMap contributors"
    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  />

  <Polyline
    positions={trajectory}
    pathOptions={{
      color: "#20ddd8",
      weight: 3,
      dashArray: "8 8",
    }}
  />

  {trajectory.map((position, index) => (
    <CircleMarker
      key={index}
      center={position}
      radius={index === trajectory.length - 1 ? 8 : 5}
      pathOptions={{
        color: "#20ddd8",
        fillColor:
          index === trajectory.length - 1
            ? "#20ddd8"
            : "#061428",
        fillOpacity: 1,
      }}
    >
      <Popup>
        {index === trajectory.length - 1
          ? "Current Location"
          : `Trajectory Point ${index + 1}`}
      </Popup>
    </CircleMarker>
  ))}
</MapContainer>
          </div>

          <div className="metadata-card">
            <h3>Float Metadata</h3>

            <div className="metadata-row">
              <span>WMO ID</span>
              <strong>{float.id}</strong>
            </div>

            <div className="metadata-row">
              <span>Institution</span>
              <strong>INCOIS</strong>
            </div>

            <div className="metadata-row">
              <span>Model</span>
              <strong>APEX</strong>
            </div>

            <div className="metadata-row">
              <span>Deployment Date</span>
              <strong>12 Jan 2024</strong>
            </div>

            <label className="profile-label">Select Profile</label>

            <select className="profile-select">
              <option>Profile #156 (Latest)</option>
              <option>Profile #155</option>
              <option>Profile #154</option>
            </select>
          </div>
        </section>

        <section className="profile-grid">
          <div className="profile-card">
            <div className="profile-card-header">
              <h3>Temperature Profile</h3>
              <span>°C vs Depth (m)</span>
            </div>

            {profile ? (
              <div className="simple-profile-chart">
                {profile.depth.map((depth, index) => (
                  <div
                    key={depth}
                    className="profile-dot temperature-dot"
                    style={{
                      left: `${profile.temperature[index] * 3}%`,
                      top: `${(depth / 1500) * 90}%`,
                    }}
                    title={`${profile.temperature[index]}°C at ${depth}m`}
                  />
                ))}
              </div>
            ) : (
              <p>No profile data</p>
            )}
          </div>

          <div className="profile-card">
            <div className="profile-card-header">
              <h3>Salinity Profile</h3>
              <span>PSU vs Depth (m)</span>
            </div>

            {profile ? (
              <div className="simple-profile-chart">
                {profile.depth.map((depth, index) => (
                  <div
                    key={depth}
                    className="profile-dot salinity-dot"
                    style={{
                      left: `${(profile.salinity[index] - 34) * 45}%`,
                      top: `${(depth / 1500) * 90}%`,
                    }}
                    title={`${profile.salinity[index]} PSU at ${depth}m`}
                  />
                ))}
              </div>
            ) : (
              <p>No profile data</p>
            )}
          </div>
        </section>

        {profile && (
          <section className="measurements-card">
            <div className="measurements-header">
              <h3>Profile Measurements (#156)</h3>
              <button>Download Data</button>
            </div>

            <table>
              <thead>
                <tr>
                  <th>Depth (m)</th>
                  <th>Temp (°C)</th>
                  <th>Salinity (PSU)</th>
                  <th>Oxygen (µmol/kg)</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {profile.depth.map((depth, index) => (
                  <tr key={depth}>
                    <td>{depth}</td>
                    <td>{profile.temperature[index]}</td>
                    <td>{profile.salinity[index]}</td>
                    <td>{210 - index * 25}</td>
                    <td>
                      <span className="good-status">● Good</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </div>
  );
}

export default FloatDetails;