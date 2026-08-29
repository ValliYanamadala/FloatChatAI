import { useState } from "react";
import Sidebar from "../components/Sidebar";
import { sendAIQuery } from "../services/api";
import VisualizationRenderer from "../components/VisualizationRenderer";

function Home() {
  const [inputVal, setInputVal] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "YOU",
      text: "Show salinity profiles in the Arabian Sea.",
    },
    {
      sender: "FLOATCHAT",
      text: "I found 32 ARGO profiles matching your request in the Arabian Sea bounding box.",
      detail: "The selected profiles contain salinity measurements from the surface to approximately 2000 m depth.",
      visualization: null,
      structuredData: null,
    },
  ]);

  const handleSend = async (textToSend) => {
    const query = (typeof textToSend === "string" ? textToSend : inputVal).trim();
    if (!query || loading) return;

    const userMsg = { sender: "YOU", text: query };
    setMessages((prev) => [...prev, userMsg]);
    setInputVal("");
    setLoading(true);

    const startTime = performance.now();

    try {
      const response = await sendAIQuery(query);
      const latencyMs = Math.round(performance.now() - startTime);

      let answerText = response.ai_context?.answer || response.ai_context?.explanation;
      if (!answerText) {
        if (response.total_matched > 0) {
          answerText = `Found ${response.total_matched} matching oceanographic measurement records across ARGO profiles.`;
        } else {
          answerText = "No matching ARGO observations found for the specified criteria.";
        }
      }

      const detailText = response.total_matched !== undefined
        ? `Matched ${response.total_matched} records from PostGIS (processed in ${latencyMs} ms).`
        : null;

      const aiMsg = {
        sender: "FLOATCHAT",
        text: answerText,
        detail: detailText,
        visualization: response.ai_context?.visualization || null,
        structuredData: response.data || [],
      };

      setMessages((prev) => [...prev, aiMsg]);

      // Persist latest query trace for Query Explanation page
      try {
        localStorage.setItem(
          "floatchat_latest_query_trace",
          JSON.stringify({
            prompt: query,
            response,
            latencyMs,
            timestamp: new Date().toISOString(),
          })
        );
      } catch {
        // Ignore localStorage quota errors
      }
    } catch (err) {
      const errorMsg = {
        sender: "FLOATCHAT",
        text: `Error processing query: ${err.message}`,
        detail: "Please verify backend server availability at localhost:8000.",
        visualization: null,
        structuredData: null,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content">
        <section className="home-hero">
          <h1>Explore the Ocean</h1>
          <h1 className="accent-title">Through Conversation</h1>

          <p className="subtitle">
            Ask questions about ARGO floats, ocean temperature,
            salinity, and marine conditions.
          </p>
        </section>

        <section className="stats-grid">
          <div className="stat-card">
            <span>ACTIVE FLOATS</span>
            <strong>3,842</strong>
            <small>● Live PostGIS</small>
          </div>

          <div className="stat-card">
            <span>OCEAN PROFILES</span>
            <strong>2.4M</strong>
            <small>Updated real-time</small>
          </div>

          <div className="stat-card">
            <span>OCEAN REGIONS</span>
            <strong>18</strong>
            <small>Global coverage</small>
          </div>

          <div className="stat-card">
            <span>MAX DEPTH</span>
            <strong>2000m</strong>
            <small>Standard core</small>
          </div>
        </section>

        <section className="analysis-terminal">
          <div className="terminal-header">
            <span>▣ ANALYSIS TERMINAL</span>
            {loading && <span style={{ color: "#20ddd8", fontSize: "0.85rem" }}>● Processing Query...</span>}
          </div>

          <div className="suggested-grid">
            <button
              disabled={loading}
              onClick={() => handleSend("What are the nearest ARGO floats to 15°N, 65°E?")}
            >
              What are the nearest ARGO floats to 15°N, 65°E?
            </button>

            <button
              disabled={loading}
              onClick={() => handleSend("Show temperature profiles in the Arabian Sea")}
            >
              Show temperature profiles in the Arabian Sea
            </button>
          </div>

          <div className="chat-area">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={msg.sender === "YOU" ? "user-message" : "ai-message"}
              >
                <span>{msg.sender}</span>
                <p>{msg.text}</p>
                {msg.detail && <small>{msg.detail}</small>}

                {msg.visualization && (
                  <VisualizationRenderer
                    spec={msg.visualization}
                    data={msg.structuredData}
                    height={280}
                  />
                )}
              </div>
            ))}

            {loading && (
              <div className="ai-message">
                <span>FLOATCHAT</span>
                <p style={{ color: "#20ddd8" }}>Querying PostGIS spatial engine & AI layer...</p>
              </div>
            )}
          </div>

          <div className="chat-input">
            <input
              type="text"
              placeholder="Ask about ARGO ocean data (e.g. 'What are the nearest ARGO floats to 15°N, 65°E?')..."
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
              disabled={loading}
            />

            <button onClick={() => handleSend()} disabled={loading}>
              {loading ? "..." : "➤"}
            </button>
          </div>

          <p className="chat-disclaimer">
            FloatChatAI generates validated spatial and oceanographic explanations backed by PostGIS.
          </p>
        </section>
      </main>
    </div>
  );
}

export default Home;