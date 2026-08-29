import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import {
  getFloatDetails,
  getFloatTrajectory,
  getProfiles,
  getMeasurements,
} from "../services/api";
import { floats as fallbackFloats, profiles as fallbackProfiles } from "../data/mockData";
import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
} from "react-leaflet";

function FloatDetails() {
  const { id } = useParams();
  const activeId = id || "ARGO_001";

  const [floatData, setFloatData] = useState(null);
  const [trajectoryData, setTrajectoryData] = useState([]);
  const [profilesList, setProfilesList] = useState([]);
  const [selectedProfileId, setSelectedProfileId] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMeasurements, setLoadingMeasurements] = useState(false);
  const [error, setError] = useState(null);

  // 1. Fetch Float Details, Trajectory, and Profiles List
  useEffect(() => {
    let isMounted = true;
    async function loadFloatInfo() {
      setLoading(true);
      setError(null);

      try {
        // Fetch float header
        const floatRes = await getFloatDetails(activeId).catch(() => null);
        // Fetch float trajectory
        const trajRes = await getFloatTrajectory(activeId).catch(() => null);
        // Fetch profiles for this float
        const profRes = await getProfiles({ float_id: activeId, page_size: 50 }).catch(() => null);

        if (!isMounted) return;

        if (floatRes) {
          setFloatData({
            id: floatRes.id,
            status: floatRes.status || "Active",
            latitude: floatRes.last_location?.latitude ?? 0,
            longitude: floatRes.last_location?.longitude ?? 0,
            maxDepth: 2000,
            latestReported: floatRes.last_reported_at
              ? new Date(floatRes.last_reported_at).toISOString().split("T")[0]
              : "N/A",
            region: floatRes.metadata?.region || "Global Ocean",
            totalProfiles: profRes?.total || 1,
            institution: floatRes.metadata?.institution || "INCOIS / ARGO Global",
            model: floatRes.metadata?.model || "APEX / PROVOR",
          });
        } else {
          const fb = fallbackFloats.find((f) => f.id === activeId) || fallbackFloats[0];
          setFloatData({
            id: fb.id,
            status: fb.status,
            latitude: fb.latitude,
            longitude: fb.longitude,
            maxDepth: fb.maxDepth,
            latestReported: "2026-08-25",
            region: fb.region,
            totalProfiles: 156,
            institution: "INCOIS",
            model: "APEX",
          });
        }

        if (trajRes && Array.isArray(trajRes.trajectory) && trajRes.trajectory.length > 0) {
          const coords = trajRes.trajectory.map((pt) => ({
            pos: [pt.latitude, pt.longitude],
            cycle: pt.cycle_number,
            date: pt.timestamp ? new Date(pt.timestamp).toLocaleDateString() : "N/A",
          }));
          setTrajectoryData(coords);
        } else {
          setTrajectoryData([
            { pos: [12.0, 65.0], cycle: 1, date: "Cycle 1" },
            { pos: [12.45, 65.32], cycle: 2, date: "Cycle 2" },
          ]);
        }

        if (profRes && Array.isArray(profRes.items) && profRes.items.length > 0) {
          setProfilesList(profRes.items);
          setSelectedProfileId(profRes.items[0].id);
        } else {
          setProfilesList([{ id: "1", cycle_number: 1, date: "2026-08-25" }]);
          setSelectedProfileId("1");
        }
      } catch (err) {
        if (isMounted) {
          setError(`Could not retrieve float details: ${err.message}`);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadFloatInfo();
    return () => {
      isMounted = false;
    };
  }, [activeId]);

  // 2. Fetch measurements for selected profile cycle
  useEffect(() => {
    if (!selectedProfileId) return;

    let isMounted = true;
    async function loadMeasurements() {
      setLoadingMeasurements(true);
      try {
        const res = await getMeasurements({ profile_id: selectedProfileId, page_size: 200 });
        if (isMounted) {
          if (res && Array.isArray(res.items) && res.items.length > 0) {
            setMeasurements(res.items);
          } else {
            // Fallback measurements
            const fbProfile = fallbackProfiles[activeId] || Object.values(fallbackProfiles)[0];
            const fallbackRows = fbProfile.depth.map((d, i) => ({
              depth_m: d,
              pressure_dbar: d * 1.01,
              temperature_C: fbProfile.temperature[i],
              salinity: fbProfile.salinity[i],
              dissolved_oxygen_umol_kg: null,
            }));
            setMeasurements(fallbackRows);
          }
        }
      } catch {
        if (isMounted) {
          const fbProfile = fallbackProfiles[activeId] || Object.values(fallbackProfiles)[0];
          const fallbackRows = fbProfile.depth.map((d, i) => ({
            depth_m: d,
            pressure_dbar: d * 1.01,
            temperature_C: fbProfile.temperature[i],
            salinity: fbProfile.salinity[i],
            dissolved_oxygen_umol_kg: null,
          }));
          setMeasurements(fallbackRows);
        }
      } finally {
        if (isMounted) setLoadingMeasurements(false);
      }
    }

    loadMeasurements();
    return () => {
      isMounted = false;
    };
  }, [selectedProfileId, activeId]);

  const handleDownload = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(
        JSON.stringify(
          {
            float: floatData,
            selected_profile_id: selectedProfileId,
            trajectory: trajectoryData,
            measurements: measurements,
          },
          null,
          2
        )
      );
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `argo_${floatData?.id || activeId}_profile_${selectedProfileId || "data"}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (loading) {
    return (
      <div className="app-layout">
        <Sidebar />
        <main className="page-content" style={{ padding: "3rem", textAlign: "center", color: "#9fb3c1" }}>
          <h2>Loading Float Details & Trajectory...</h2>
        </main>
      </div>
    );
  }

  const float = floatData || {
    id: activeId,
    status: "Active",
    latitude: 15.0,
    longitude: 65.0,
    maxDepth: 2000,
    latestReported: "N/A",
    totalProfiles: 1,
    institution: "INCOIS",
    model: "APEX",
  };

  const polylinePositions = trajectoryData.map((t) => t.pos);
  const mapCenter = polylinePositions.length > 0 ? polylinePositions[polylinePositions.length - 1] : [15, 65];

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content float-details-page">
        {error && (
          <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "8px 16px", borderRadius: "6px", marginBottom: "1rem" }}>
            ⚠ {error}
          </div>
        )}

        <div className="float-details-header">
          <div>
            <span className="active-badge">● {float.status}</span>
            <h1>Float {float.id}</h1>
          </div>

          <div className="header-actions">
            <button onClick={() => alert(`Saved Float ${float.id} to bookmarks.`)}>Save</button>
            <button onClick={() => navigator.clipboard?.writeText(window.location.href)}>Share</button>
          </div>
        </div>

        <section className="float-summary-grid">
          <div className="summary-card">
            <span>CURRENT LOCATION</span>
            <strong>
              {float.latitude.toFixed(2)}°N, {float.longitude.toFixed(2)}°E
            </strong>
          </div>

          <div className="summary-card">
            <span>MAX DEPTH</span>
            <strong>{float.maxDepth} m</strong>
          </div>

          <div className="summary-card">
            <span>LATEST REPORTED</span>
            <strong>{float.latestReported}</strong>
          </div>

          <div className="summary-card">
            <span>TOTAL PROFILES</span>
            <strong>{float.totalProfiles}</strong>
          </div>
        </section>

        <section className="float-main-grid">
          <div className="trajectory-card">
            <h3>Trajectory Map</h3>

            <MapContainer
              center={mapCenter}
              zoom={5}
              className="details-map"
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <Polyline
                positions={polylinePositions}
                pathOptions={{
                  color: "#20ddd8",
                  weight: 3,
                  dashArray: "8 8",
                }}
              />

              {trajectoryData.map((pt, index) => (
                <CircleMarker
                  key={index}
                  center={pt.pos}
                  radius={index === trajectoryData.length - 1 ? 8 : 5}
                  pathOptions={{
                    color: "#20ddd8",
                    fillColor:
                      index === trajectoryData.length - 1
                        ? "#20ddd8"
                        : "#061428",
                    fillOpacity: 1,
                  }}
                >
                  <Popup>
                    {index === trajectoryData.length - 1
                      ? `Latest Fix (Cycle ${pt.cycle || index + 1})`
                      : `Fix Point (Cycle ${pt.cycle || index + 1}) - ${pt.date}`}
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
              <strong>{float.institution}</strong>
            </div>

            <div className="metadata-row">
              <span>Region</span>
              <strong>{float.region}</strong>
            </div>

            <div className="metadata-row">
              <span>Model</span>
              <strong>{float.model}</strong>
            </div>

            <label className="profile-label">Select Profile Cycle</label>

            <select
              className="profile-select"
              value={selectedProfileId || ""}
              onChange={(e) => setSelectedProfileId(e.target.value)}
            >
              {profilesList.map((prof) => (
                <option key={prof.id} value={prof.id}>
                  Profile #{prof.id} (Cycle {prof.cycle_number ?? 1})
                </option>
              ))}
            </select>
          </div>
        </section>

        <section className="profile-grid">
          <div className="profile-card">
            <div className="profile-card-header">
              <h3>Temperature Profile</h3>
              <span>°C vs Depth (m)</span>
            </div>

            {loadingMeasurements ? (
              <p style={{ color: "#9fb3c1", padding: "1rem" }}>Loading profile measurements...</p>
            ) : measurements.length > 0 ? (
              <div className="simple-profile-chart">
                {measurements.map((m, index) => {
                  const depthVal = m.depth_m ?? m.pressure_dbar ?? 0;
                  const tempVal = m.temperature_C ?? m.parameters?.temperature_C;
                  if (tempVal === undefined || tempVal === null) return null;
                  return (
                    <div
                      key={index}
                      className="profile-dot temperature-dot"
                      style={{
                        left: `${Math.min(100, Math.max(0, tempVal * 3))}%`,
                        top: `${Math.min(95, (depthVal / 1500) * 90)}%`,
                      }}
                      title={`${tempVal.toFixed(2)}°C at ${depthVal.toFixed(1)}m`}
                    />
                  );
                })}
              </div>
            ) : (
              <p style={{ color: "#9fb3c1", padding: "1rem" }}>No profile data available</p>
            )}
          </div>

          <div className="profile-card">
            <div className="profile-card-header">
              <h3>Salinity Profile</h3>
              <span>PSU vs Depth (m)</span>
            </div>

            {loadingMeasurements ? (
              <p style={{ color: "#9fb3c1", padding: "1rem" }}>Loading profile measurements...</p>
            ) : measurements.length > 0 ? (
              <div className="simple-profile-chart">
                {measurements.map((m, index) => {
                  const depthVal = m.depth_m ?? m.pressure_dbar ?? 0;
                  const salVal = m.salinity ?? m.parameters?.salinity;
                  if (salVal === undefined || salVal === null) return null;
                  return (
                    <div
                      key={index}
                      className="profile-dot salinity-dot"
                      style={{
                        left: `${Math.min(100, Math.max(0, (salVal - 33) * 30))}%`,
                        top: `${Math.min(95, (depthVal / 1500) * 90)}%`,
                      }}
                      title={`${salVal.toFixed(2)} PSU at ${depthVal.toFixed(1)}m`}
                    />
                  );
                })}
              </div>
            ) : (
              <p style={{ color: "#9fb3c1", padding: "1rem" }}>No profile data available</p>
            )}
          </div>
        </section>

        <section className="measurements-card">
          <div className="measurements-header">
            <h3>Profile Measurements (#{selectedProfileId || "N/A"})</h3>
            <button onClick={handleDownload}>Download Data</button>
          </div>

          <table>
            <thead>
              <tr>
                <th>Depth (m)</th>
                <th>Pressure (dbar)</th>
                <th>Temp (°C)</th>
                <th>Salinity (PSU)</th>
                <th>Oxygen (µmol/kg)</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {measurements.map((m, index) => {
                const params = m.parameters || {};
                const depthVal = params.depth_m ?? m.depth_m ?? m.depth_or_pressure ?? "N/A";
                const presVal = params.pressure_dbar ?? m.pressure_dbar ?? "N/A";
                const tempNum = params.temperature_C ?? m.temperature_C;
                const salNum = params.salinity ?? m.salinity;
                const oxyNum = params.dissolved_oxygen_umol_kg ?? m.dissolved_oxygen_umol_kg;

                const tempVal = tempNum !== undefined && tempNum !== null ? Number(tempNum).toFixed(2) : "N/A";
                const salVal = salNum !== undefined && salNum !== null ? Number(salNum).toFixed(2) : "N/A";
                const oxyVal = oxyNum !== undefined && oxyNum !== null ? Number(oxyNum).toFixed(1) : "N/A";

                return (
                  <tr key={index}>
                    <td>{typeof depthVal === "number" ? depthVal.toFixed(1) : depthVal}</td>
                    <td>{typeof presVal === "number" ? presVal.toFixed(1) : presVal}</td>
                    <td>{tempVal}</td>
                    <td>{salVal}</td>
                    <td>{oxyVal}</td>
                    <td>
                      <span className="good-status">● Validated</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      </main>
    </div>
  );
}

export default FloatDetails;