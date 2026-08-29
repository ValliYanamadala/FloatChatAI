import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { floats } from "../data/mockData";
import {

    MapContainer,
  
    TileLayer,
  
    Marker,
  
    Popup,
  
  } from "react-leaflet";

function Explorer() {
  const navigate = useNavigate();

  const [searchId, setSearchId] = useState("");
  const [selectedRegions, setSelectedRegions] = useState([
    "Arabian Sea",
    "Bay of Bengal",
  ]);
  const [selectedFeatures, setSelectedFeatures] = useState([
    "Temp",
    "Salinity",
  ]);
  const [depth, setDepth] = useState(2000);
  const [status, setStatus] = useState("Active");
  const [selectedFloats, setSelectedFloats] = useState([]);

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
    return floats.filter((float) => {
      const matchesId = float.id.includes(searchId);

      const matchesRegion =
        selectedRegions.length === 0 ||
        selectedRegions.includes(float.region);

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

        <label>Float ID</label>

        <input
          type="text"
          placeholder="e.g. 2901234"
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          className="filter-input"
        />

        <label>Region</label>

        {[
          "Arabian Sea",
          "Bay of Bengal",
          "Indian Ocean (Equatorial)",
          "Southern Ocean",
        ].map((region) => (
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
          className="reset-btn"
          onClick={resetFilters}
        >
          Reset Filters
        </button>
      </aside>

      <main className="explorer-main">
      <section className="real-map-wrapper">
  <MapContainer
    center={[10, 75]}
    zoom={4}
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
      >
        <Popup>
          <div className="map-popup">
            <h3>Float {float.id}</h3>

            <p>
              <strong>Region:</strong> {float.region}
            </p>

            <p>
              <strong>Position:</strong>{" "}
              {float.latitude}°, {float.longitude}°
            </p>

            <p>
              <strong>Status:</strong> {float.status}
            </p>

            <p>
              <strong>Features:</strong>{" "}
              {float.features.join(", ")}
            </p>

            <p>
              <strong>Latest Reading:</strong>{" "}
              {float.latestReading}°C
            </p>

            <button
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
              {filteredFloats.length} floats found
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

          <div className="result-list">
            {filteredFloats.map((float) => (
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
                    {float.latitude}°N, {float.longitude}°E
                  </span>
                </div>

                <div>
                  <small>LAST READING</small>
                  <strong className="cyan">
                    {float.latestReading}°C
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
                  className="view-details-btn"
                  onClick={() =>
                    navigate(`/float/${float.id}`)
                  }
                >
                  View Details →
                </button>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default Explorer;