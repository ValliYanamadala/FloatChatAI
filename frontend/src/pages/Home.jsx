import { useState } from "react";
import Sidebar from "../components/Sidebar";

function Home() {
  const [inputVal, setInputVal] = useState("");
  const [messages, setMessages] = useState([
    {
      sender: "YOU",
      text: "Show salinity profiles in the Arabian Sea.",
    },
    {
      sender: "FLOATCHAT",
      text: "I found 32 ARGO profiles matching your request in the Arabian Sea bounding box.",
      detail: "The selected profiles contain salinity measurements from the surface to approximately 2000 m depth.",
    },
  ]);

  const handleSend = (textToSend) => {
    const query = (typeof textToSend === "string" ? textToSend : inputVal).trim();
    if (!query) return;

    const userMsg = { sender: "YOU", text: query };
    let aiMsg = {
      sender: "FLOATCHAT",
      text: `Analyzed ocean request for: "${query}".`,
      detail: "Retrieved corresponding ARGO float profiles and sensor data.",
    };

    const lower = query.toLowerCase();
    if (lower.includes("temperature") || lower.includes("arabian sea")) {
      aiMsg = {
        sender: "FLOATCHAT",
        text: "Retrieved temperature profiles in the Arabian Sea from surface to 2000 dbar.",
        detail: "Mean surface temperature: 27.8°C with typical tropical thermocline structure.",
      };
    } else if (lower.includes("india") || lower.includes("active") || lower.includes("nearest")) {
      aiMsg = {
        sender: "FLOATCHAT",
        text: "Identified active ARGO profiling floats in the Northern Indian Ocean basin.",
        detail: "Active platforms: 2901234, 2901240, 2901278 actively reporting daily cycles.",
      };
    }

    setMessages((prev) => [...prev, userMsg, aiMsg]);
    setInputVal("");
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
            <small>● Live</small>
          </div>

          <div className="stat-card">
            <span>OCEAN PROFILES</span>
            <strong>2.4M</strong>
            <small>Updated hourly</small>
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
          </div>

          <div className="suggested-grid">
            <button onClick={() => handleSend("Show temperature profiles in the Arabian Sea")}>
              Show temperature profiles in the Arabian Sea
            </button>

            <button onClick={() => handleSend("Find active ARGO floats near India")}>
              Find active ARGO floats near India
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
              </div>
            ))}
          </div>

          <div className="chat-input">
            <input
              type="text"
              placeholder="Ask about ARGO ocean data..."
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSend();
              }}
            />

            <button onClick={() => handleSend()}>➤</button>
          </div>

          <p className="chat-disclaimer">
            FloatChat may produce inaccurate information about specific sensor deployments.
          </p>
        </section>
      </main>
    </div>
  );
}

export default Home;