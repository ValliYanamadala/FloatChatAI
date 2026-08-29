import Sidebar from "../components/Sidebar";

function Home() {
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
            <button>
              Show temperature profiles in the Arabian Sea
            </button>

            <button>
              Find active ARGO floats near India
            </button>
          </div>

          <div className="chat-area">
            <div className="user-message">
              <span>YOU</span>
              <p>Show salinity profiles in the Arabian Sea.</p>
            </div>

            <div className="ai-message">
              <span>FLOATCHAT</span>
              <p>
                I found 32 ARGO profiles matching your request
                in the Arabian Sea bounding box.
              </p>

              <small>
                The selected profiles contain salinity measurements
                from the surface to approximately 2000 m depth.
              </small>
            </div>
          </div>

          <div className="chat-input">
            <input
              type="text"
              placeholder="Ask about ARGO ocean data..."
            />

            <button>➤</button>
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