import { useLocation, useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function Analytics() {
  const location = useLocation();
  const navigate = useNavigate();

  const {
    selectedFloats = [],
    selectedFeatures = [],
    selectedRegions = [],
    depth = 2000,
    status = "All",
  } = location.state || {};

  const floatA = selectedFloats[0];
  const floatB = selectedFloats[1];

  const hasComparison = Boolean(floatA && floatB);

  const temperatureData = [
    { depth: 0, floatA: 28.1, floatB: 26.8 },
    { depth: 100, floatA: 24.5, floatB: 23.9 },
    { depth: 500, floatA: 18.2, floatB: 17.5 },
    { depth: 1000, floatA: 9.4, floatB: 8.8 },
    { depth: 1500, floatA: 4.8, floatB: 4.5 },
  ];

  const timeData = [
    { month: "Mar", floatA: 27.0, floatB: 26.1 },
    { month: "Apr", floatA: 27.5, floatB: 26.4 },
    { month: "May", floatA: 28.1, floatB: 26.8 },
    { month: "Jun", floatA: 27.8, floatB: 26.5 },
    { month: "Jul", floatA: 28.3, floatB: 26.9 },
    { month: "Aug", floatA: 27.3, floatB: 26.8 },
  ];

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content analytics-page">
        <h1>Comparative Analytics</h1>

        <p className="subtitle">
          Analyze selected ARGO floats and compare ocean measurements.
        </p>

        <section className="analytics-summary">
          <div className="summary-card">
            <span>FLOAT A</span>
            <strong>{floatA || "Not selected"}</strong>
          </div>

          <div className="summary-card">
            <span>FLOAT B</span>
            <strong>{floatB || "Not selected"}</strong>
          </div>

          <div className="summary-card">
            <span>FEATURES</span>
            <strong>
              {selectedFeatures.length
                ? selectedFeatures.join(", ")
                : "None"}
            </strong>
          </div>

          <div className="summary-card">
            <span>DEPTH RANGE</span>
            <strong>0 - {depth} m</strong>
          </div>
        </section>

        <section className="analytics-info">
          <div>
            <span>Region</span>
            <strong>
              {selectedRegions.length
                ? selectedRegions.join(", ")
                : "All"}
            </strong>
          </div>

          <div>
            <span>Status</span>
            <strong>{status}</strong>
          </div>
        </section>
        <section className="analytics-controls">

  <div className="control-group">
    <label>PARAMETER</label>

    <select>
      <option>Temperature (°C)</option>
      <option>Salinity (PSU)</option>
      <option>Oxygen</option>
      <option>Chlorophyll</option>
    </select>
  </div>

  <div className="control-group">
    <label>FLOAT A</label>

    <select defaultValue={floatA || ""}>
      <option value="">Select Float</option>
      <option value="2901234">2901234</option>
      <option value="2901240">2901240</option>
      <option value="2901266">2901266</option>
    </select>
  </div>

  <div className="control-group">
    <label>FLOAT B</label>

    <select defaultValue={floatB || ""}>
      <option value="">Select Float</option>
      <option value="2901234">2901234</option>
      <option value="2901240">2901240</option>
      <option value="2901266">2901266</option>
    </select>
  </div>

  <div className="control-group">
    <label>TIME PERIOD</label>

    <select>
      <option>Last 6 Months</option>
      <option>Last 3 Months</option>
      <option>Last 1 Year</option>
      <option>Custom Range</option>
    </select>
  </div>

  <div className="control-group">
    <label>DEPTH RANGE</label>

    <select defaultValue={depth}>
      <option value="500">0 - 500 m</option>
      <option value="1000">0 - 1000 m</option>
      <option value="1500">0 - 1500 m</option>
      <option value="2000">0 - 2000 m</option>
    </select>
  </div>

  <button className="compare-control-btn">
    Compare
  </button>

</section>

        {hasComparison ? (
          <section className="analytics-charts">
            <div className="chart-card">
              <h3>Temperature vs Depth</h3>

              <ResponsiveContainer width="100%" height={380}>
                <LineChart
                  data={temperatureData}
                  layout="vertical"
                  margin={{
                    top: 20,
                    right: 30,
                    left: 20,
                    bottom: 20,
                  }}
                >
                  <CartesianGrid
                    stroke="#173149"
                    strokeDasharray="3 3"
                  />

                  <XAxis
                    type="number"
                    domain={[0, 30]}
                    stroke="#9fb3c1"
                    label={{
                      value: "Temperature (°C)",
                      position: "insideBottom",
                      offset: -10,
                    }}
                  />

                  <YAxis
                    dataKey="depth"
                    type="number"
                    reversed
                    domain={[0, 1500]}
                    stroke="#9fb3c1"
                    label={{
                      value: "Depth (m)",
                      angle: -90,
                      position: "insideLeft",
                    }}
                  />

                  <Tooltip />
                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="floatA"
                    name={`Float ${floatA}`}
                    stroke="#20ddd8"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />

                  <Line
                    type="monotone"
                    dataKey="floatB"
                    name={`Float ${floatB}`}
                    stroke="#9fb7ff"
                    strokeWidth={3}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="analytics-right">
              <div className="ai-insight-card">
                <span>AI INSIGHT</span>

                <p>
                  Float {floatA} recorded warmer surface temperatures
                  than Float {floatB} across the selected period.
                </p>
              </div>

              <div className="chart-card">
                <h3>Surface Temperature Over Time</h3>

                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={timeData}
                    margin={{
                      top: 20,
                      right: 20,
                      left: 0,
                      bottom: 10,
                    }}
                  >
                    <CartesianGrid
                      stroke="#173149"
                      strokeDasharray="3 3"
                    />

                    <XAxis
                      dataKey="month"
                      stroke="#9fb3c1"
                    />

                    <YAxis
                      stroke="#9fb3c1"
                      domain={[20, 30]}
                    />

                    <Tooltip />
                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="floatA"
                      name={`Float ${floatA}`}
                      stroke="#20ddd8"
                      strokeWidth={3}
                      dot={{ r: 4 }}
                    />

                    <Line
                      type="monotone"
                      dataKey="floatB"
                      name={`Float ${floatB}`}
                      stroke="#9fb7ff"
                      strokeWidth={3}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>
        ) : (
          <div className="analytics-empty-state">
            <div className="analytics-empty-icon">⌁</div>

            <h2>No Floats Selected</h2>

            <p>
              Select two ARGO floats from Explorer to compare their
              temperature, salinity, and depth measurements.
            </p>

            <button
              className="select-floats-btn"
              onClick={() => navigate("/explorer")}
            >
              Select Floats in Explorer →
            </button>

            <div className="analytics-empty-steps">
              <span>
                <strong>1</strong> Open Explorer
              </span>

              <span>
                <strong>2</strong> Select two floats
              </span>

              <span>
                <strong>3</strong> Compare results
              </span>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Analytics;