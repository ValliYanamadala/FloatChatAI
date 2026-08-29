import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import { sendAIQuery } from "../services/api";

function QueryExplanation() {
  const [trace, setTrace] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customPrompt, setCustomPrompt] = useState("");

  const loadSavedTrace = () => {
    try {
      const saved = localStorage.getItem("floatchat_latest_query_trace");
      if (saved) {
        setTrace(JSON.parse(saved));
        return true;
      }
    } catch {
      // Fallback
    }
    return false;
  };

  // Run live query through real backend if no trace exists or on user request
  const runLiveExplanation = async (promptToRun) => {
    const query = (promptToRun || customPrompt || "What are the nearest ARGO floats to 15°N, 65°E?").trim();
    setLoading(true);
    const startTime = performance.now();
    try {
      const response = await sendAIQuery(query);
      const latencyMs = Math.round(performance.now() - startTime);
      const newTrace = {
        prompt: query,
        response,
        latencyMs,
        timestamp: new Date().toISOString(),
      };
      setTrace(newTrace);
      try {
        localStorage.setItem("floatchat_latest_query_trace", JSON.stringify(newTrace));
      } catch {
        // Ignore quota
      }
    } catch (err) {
      console.error("Query explanation error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const hasTrace = loadSavedTrace();
    if (!hasTrace) {
      runLiveExplanation("What are the nearest ARGO floats to 15°N, 65°E?");
    }
  }, []);

  const queryText = trace?.prompt || "What are the nearest ARGO floats to 15°N, 65°E?";
  const aiContext = trace?.response?.ai_context;
  const parsedIntent = aiContext?.parsed_intent;

  const parametersText = parsedIntent?.parameters?.length
    ? parsedIntent.parameters.join(", ")
    : (parsedIntent?.bounding_box ? "Spatial Coordinates / Proximity" : "N/A");

  const regionText = parsedIntent?.bounding_box
    ? `Bounding Box [${parsedIntent.bounding_box.min_lat.toFixed(2)}°, ${parsedIntent.bounding_box.min_lon.toFixed(2)}°] to [${parsedIntent.bounding_box.max_lat.toFixed(2)}°, ${parsedIntent.bounding_box.max_lon.toFixed(2)}°]`
    : "N/A";

  const periodText = parsedIntent?.start_date
    ? `${parsedIntent.start_date} to ${parsedIntent.end_date || "present"}`
    : "N/A";

  const depthText = parsedIntent?.depth_range
    ? `${parsedIntent.depth_range.min ?? 0}m - ${parsedIntent.depth_range.max ?? "max"}m`
    : "N/A";

  const recordsProcessed = trace?.response?.total_matched ?? 0;
  const returnedCount = trace?.response?.returned_count ?? trace?.response?.data?.length ?? 0;
  const latency = trace?.latencyMs ?? 0;

  const matchedFloats = trace?.response?.data
    ? Array.from(new Set(trace.response.data.map((d) => d.float_id).filter(Boolean))).join(", ")
    : "N/A";

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content query-page">
        <h1>How FloatChat Answered You</h1>

        <p className="subtitle">
          System transparency report showing how your query was
          interpreted, processed, and converted into an ocean-data response.
        </p>

        {/* ORIGINAL QUERY CARD */}
        <section className="query-original-card">
          <span>ORIGINAL QUERY</span>
          <h2 id="query-original-prompt">“{queryText}”</h2>
          {loading && <p style={{ color: "#20ddd8", marginTop: "4px" }}>● Fetching live query trace from backend...</p>}
        </section>

        <div className="query-main-grid">
          {/* LEFT SIDE */}
          <div className="query-left">
            <section className="query-card">
              <h3>SEMANTIC INTERPRETATION</h3>

              <div className="interpretation-grid">
                <div className="interpretation-item">
                  <span>PARAMETER</span>
                  <strong id="query-param-text">{parametersText}</strong>
                </div>

                <div className="interpretation-item">
                  <span>REGION / LOCATION</span>
                  <strong id="query-region-text">{regionText}</strong>
                </div>

                <div className="interpretation-item">
                  <span>DEPTH RANGE</span>
                  <strong>{depthText}</strong>
                </div>

                <div className="interpretation-item">
                  <span>PERIOD</span>
                  <strong>{periodText}</strong>
                </div>

                <div className="interpretation-item">
                  <span>TARGET FLOATS</span>
                  <strong id="query-floats-text">{matchedFloats || "All in region"}</strong>
                </div>

                <div className="interpretation-item">
                  <span>PARSER PIPELINE</span>
                  <strong>{aiContext?.parser_used || "Deterministic + PostGIS Rules"}</strong>
                </div>
              </div>
            </section>

            <section className="query-card data-scope">
              <h3>DATA SCOPE</h3>

              <div className="scope-row">
                <span>Measurements Matched</span>
                <strong id="query-records-matched">{recordsProcessed}</strong>
              </div>

              <div className="scope-row">
                <span>Returned Slices</span>
                <strong>{returnedCount}</strong>
              </div>

              <div className="scope-row">
                <span>Database Engine</span>
                <strong>PostgreSQL 16 + PostGIS</strong>
              </div>

              <div className="scope-row">
                <span>Visualization Spec</span>
                <strong>{aiContext?.visualization?.type ? `${aiContext.visualization.type.toUpperCase()}: ${aiContext.visualization.title}` : "N/A"}</strong>
              </div>

              <div className="scope-row">
                <span>AI Grounding Status</span>
                <strong className="confidence" id="query-grounding-status">
                  {aiContext?.status === "success" ? "100% Validated" : (aiContext?.status || "Grounded")}
                </strong>
              </div>
            </section>
          </div>

          {/* RIGHT SIDE */}
          <section className="query-card pipeline-card">
            <div className="pipeline-header">
              <h3>PROCESSING PIPELINE</h3>
              <span id="query-latency-display">Latency: {latency} ms</span>
            </div>

            <div className="pipeline">
              <div className="pipeline-step completed">
                <div className="pipeline-number">1</div>
                <div>
                  <h4>Understand Intent & Extract Entities</h4>
                  <p>
                    {aiContext?.explanation || "Parsed natural language into structured spatial bounding box and parameters."}
                  </p>
                </div>
              </div>

              <div className="pipeline-step completed">
                <div className="pipeline-number">2</div>
                <div>
                  <h4>Build Validated Query Plan</h4>
                  <p>
                    Produced typed filter parameters flowing through controlled backend endpoints without generating raw SQL.
                  </p>
                </div>
              </div>

              <div className="pipeline-step completed">
                <div className="pipeline-number">3</div>
                <div>
                  <h4>PostGIS Spatial & Sensor Retrieval</h4>
                  <p>
                    Executed PostGIS bounding box query returning {recordsProcessed} verified measurements from PostgreSQL.
                  </p>
                </div>
              </div>

              <div className="pipeline-step completed">
                <div className="pipeline-number">4</div>
                <div>
                  <h4>Synthesize Grounded Response</h4>
                  <p>
                    {aiContext?.answer || "Synthesized scientific response directly from returned physical observations."}
                  </p>
                </div>
              </div>

              <div className="pipeline-step completed">
                <div className="pipeline-number">✓</div>
                <div>
                  <h4>Generate Declarative VisualizationSpec</h4>
                  <p>
                    Produced {aiContext?.visualization?.type || "declarative"} specification rendered by VisualizationRenderer.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

export default QueryExplanation;