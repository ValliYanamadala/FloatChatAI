import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import L from "leaflet";
import iconUrl from "leaflet/dist/images/marker-icon.png";
import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
import shadowUrl from "leaflet/dist/images/marker-shadow.png";
import Sidebar from "../components/Sidebar";
import { getFloats } from "../services/api";
import { floats as fallbackFloats } from "../data/mockData";
import { getExplorerState, saveExplorerState } from "../utils/storage";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

const defaultMarkerIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});

const AVAILABLE_REGIONS = [
  "Arabian Sea",
  "Indian Ocean",
  "North Atlantic",
  "South Atlantic",
  "North Pacific",
  "South Pacific",
  "Southern Ocean",
  "Arctic/North Atlantic",
];

function Explorer() {
  const navigate = useNavigate();
  const savedState = getExplorerState() || {};

  const [floatsData, setFloatsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState(null);

  const [searchId, setSearchId] = useState(savedState.searchId || "");
  const [selectedRegions, setSelectedRegions] = useState(savedState.selectedRegions || []);
  const [selectedFeatures, setSelectedFeatures] = useState(savedState.selectedFeatures || []);
  const [depth, setDepth] = useState(savedState.depth || 2000);
  const [status, setStatus] = useState(savedState.status || "All");
  const [selectedFloats, setSelectedFloats] = useState([]);

  // Fetch real floats from backend API
  useEffect(() => {
    let isMounted = true;
    async function loadFloats() {
      setLoading(true);
      setApiError(null);
      try {
        const response = await getFloats({ page: 1, page_size: 100 });
        if (isMounted) {
          if (response && Array.isArray(response.items) && response.items.length > 0) {
            const transformed = response.items.map((item) => ({
              id: item.id,
              latitude: item.last_location?.latitude ?? 0,
              longitude: item.last_location?.longitude ?? 0,
              region: item.metadata?.region || "N/A",
              status: item.status || "Active",
              maxDepth: 2000,
              latestReading: item.last_reported_at
                ? new Date(item.last_reported_at).toISOString().split("T")[0]
                : "N/A",
              features: ["Temp", "Salinity", "Oxygen"],
            }));
            setFloatsData(transformed);
          } else {
            setFloatsData(fallbackFloats);
          }
        }
      } catch (err) {
        if (isMounted) {
          setApiError(`Live backend unavailable: ${err.message}. Using cached baseline data.`);
          setFloatsData(fallbackFloats);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadFloats();
    return () => {
      isMounted = false;
    };
  }, []);

  // Persist explorer filter state
  useEffect(() => {
    saveExplorerState({
      searchId,
      selectedRegions,
      selectedFeatures,
      depth,
      status,
    });
  }, [searchId, selectedRegions, selectedFeatures, depth, status]);

  const toggleRegion = (region) => {
    setSelectedRegions((prev) =>
      prev.includes(region)
        ? prev.filter((item) => item !== region)
        : [...prev, region]
    );
  };

  const toggleFeature = (feature) => {
    setSelectedFeatures((prev) =>
      prev.includes(feature)
        ? prev.filter((item) => item !== feature)
        : [...prev, feature]
    );
  };

  const toggleFloat = (id) => {
    setSelectedFloats((prev) =>
      prev.includes(id)
        ? prev.filter((item) => item !== id)
        : [...prev, id]
    );
  };

  const filteredFloats = useMemo(() => {
    return floatsData.filter((float) => {
      const matchesId = !searchId.trim() || float.id.toLowerCase().includes(searchId.trim().toLowerCase());

      const matchesRegion =
        selectedRegions.length === 0 ||
        selectedRegions.some(
          (reg) =>
            float.region.toLowerCase().includes(reg.toLowerCase()) ||
            reg.toLowerCase().includes(float.region.toLowerCase())
        );

      const matchesFeatures =
        selectedFeatures.length === 0 ||
        selectedFeatures.every((feature) =>
          float.features.includes(feature)
        );

      const matchesDepth = float.maxDepth >= depth;

      const matchesStatus =
        status === "All" || float.status === status;

      return (
        matchesId &&
        matchesRegion &&
        matchesFeatures &&
        matchesDepth &&
        matchesStatus
      );
    });
  }, [
    floatsData,
    searchId,
    selectedRegions,
    selectedFeatures,
    depth,
    status,
  ]);

  const resetFilters = () => {
    setSearchId("");
    setSelectedRegions([]);
    setSelectedFeatures([]);
    setDepth(2000);
    setStatus("All");
    setSelectedFloats([]);
  };

  const compareSelected = () => {
    navigate("/analytics", {
      state: {
        selectedFloats,
        selectedFeatures,
        selectedRegions,
        depth,
        status,
      },
    });
  };

  return (
    <div className="app-layout">
      <Sidebar />

      <aside className="explorer-filters">
        <div className="filter-title">
          <span>☰</span>
          <h2>Search Parameters</h2>
        </div>

        <label htmlFor="search-float-id">Float ID</label>

        <input
          id="search-float-id"
          type="text"
          placeholder="e.g. ARGO_010 or ARGO_001"
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          className="filter-input"
        />

        <label>Region</label>

        {AVAILABLE_REGIONS.map((region) => (
          <label className="check-row" key={region}>
            <input
              type="checkbox"
              checked={selectedRegions.includes(region)}
              onChange={() => toggleRegion(region)}
            />
            {region}
          </label>
        ))}

        <label>Features Available</label>

        <div className="feature-grid">
          {["Temp", "Salinity", "Oxygen", "Chlorophyll"].map(
            (feature) => (
              <button
                key={feature}
                type="button"
                className={
                  selectedFeatures.includes(feature)
                    ? "feature-btn active"
                    : "feature-btn"
                }
                onClick={() => toggleFeature(feature)}
              >
                {feature}
              </button>
            )
          )}
        </div>

        <div className="depth-title">
          <label>Depth Range</label>
          <span>0m - {depth}m</span>
        </div>

        <input
          type="range"
          min="500"
          max="2000"
          step="100"
          value={depth}
          onChange={(e) => setDepth(Number(e.target.value))}
          className="depth-slider"
        />

        <label>Status</label>

        <div className="status-row">
          {["Active", "Inactive", "All"].map((item) => (
            <label key={item}>
              <input
                type="radio"
                name="status"
                checked={status === item}
                onChange={() => setStatus(item)}
              />
              {item}
            </label>
          ))}
        </div>

        <button
          id="reset-filters-btn"
          type="button"
          className="reset-btn"
          onClick={resetFilters}
        >
          Reset Filters
        </button>
      </aside>

      <main className="explorer-main">
        {apiError && (
          <div style={{ background: "rgba(239, 68, 68, 0.15)", border: "1px solid #ef4444", color: "#fca5a5", padding: "8px 16px", borderRadius: "6px", margin: "8px 16px" }}>
            ⚠ {apiError}
          </div>
        )}

        <section className="real-map-wrapper">
          <MapContainer
            center={[15, 65]}
            zoom={3}
            className="real-map"
          >
            <TileLayer
              attribution="&copy; OpenStreetMap contributors"
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {filteredFloats.map((float) => (
              <Marker
                key={float.id}
                position={[float.latitude, float.longitude]}
                icon={defaultMarkerIcon}
              >
                <Popup>
                  <div className="map-popup">
                    <h3>Float {float.id}</h3>

                    <p>
                      <strong>Region:</strong> {float.region}
                    </p>

                    <p>
                      <strong>Position:</strong>{" "}
                      {float.latitude.toFixed(2)}°, {float.longitude.toFixed(2)}°
                    </p>

                    <p>
                      <strong>Status:</strong> {float.status}
                    </p>

                    <p>
                      <strong>Features:</strong>{" "}
                      {float.features.join(", ")}
                    </p>

                    <p>
                      <strong>Last Reported:</strong>{" "}
                      {float.latestReading}
                    </p>

                    <button
                      id={`popup-view-details-${float.id}`}
                      className="popup-details-btn"
                      onClick={() =>
                        navigate(`/float/${float.id}`)
                      }
                    >
                      View Details →
                    </button>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </section>

        <section className="results-panel">
          <div className="results-header">
            <h3>▦ Search Results</h3>
            <span>
              {loading ? "Loading floats..." : `${filteredFloats.length} floats found`}
            </span>
          </div>

          {selectedFloats.length >= 2 && (
            <div className="compare-bar">
              <span>
                {selectedFloats.length} floats selected
              </span>

              <button onClick={compareSelected}>
                Compare Selected →
              </button>
            </div>
          )}

          <div className="result-list" id="explorer-results-list">
            {loading ? (
              <div style={{ padding: "2rem", color: "#9fb3c1", textAlign: "center" }}>
                Loading ARGO float dataset from PostGIS...
              </div>
            ) : filteredFloats.length === 0 ? (
              <div style={{ padding: "2rem", color: "#9fb3c1", textAlign: "center" }}>
                <p>No floats match the selected filters.</p>
                <button className="reset-btn" style={{ margin: "1rem auto", width: "auto" }} onClick={resetFilters}>
                  Reset Filters
                </button>
              </div>
            ) : (
              filteredFloats.map((float) => (
                <div className="result-card" key={float.id}>
                  <input
                    type="checkbox"
                    checked={selectedFloats.includes(float.id)}
                    onChange={() => toggleFloat(float.id)}
                  />

                  <div>
                    <small>FLOAT ID</small>
                    <strong>{float.id}</strong>
                  </div>

                  <div>
                    <small>POSITION</small>
                    <span>
                      {float.latitude.toFixed(2)}°N, {float.longitude.toFixed(2)}°E
                    </span>
                  </div>

                  <div>
                    <small>REGION</small>
                    <span style={{ color: "#9fb3c1" }}>
                      {float.region}
                    </span>
                  </div>

                  <div>
                    <small>LAST REPORTED</small>
                    <strong className="cyan">
                      {float.latestReading}
                    </strong>
                  </div>

                  <span
                    className={
                      float.status === "Active"
                        ? "status-pill active"
                        : "status-pill"
                    }
                  >
                    {float.status}
                  </span>

                  <button
                    id={`card-view-details-${float.id}`}
                    className="view-details-btn"
                    onClick={() =>
                      navigate(`/float/${float.id}`)
                    }
                  >
                    View Details →
                  </button>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default Explorer;