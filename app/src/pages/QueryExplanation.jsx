import Sidebar from "../components/Sidebar";

function QueryExplanation() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="page-content query-page">
        <h1>How FloatChat Answered You</h1>

        <p className="subtitle">
          System transparency report showing how your query was
          interpreted, processed, and converted into an ocean-data response.
        </p>

        {/* ORIGINAL QUERY */}

        <section className="query-original-card">
          <span>ORIGINAL QUERY</span>

          <h2>
            “Compare salinity in the Arabian Sea during the last six months.”
          </h2>
        </section>

        <div className="query-main-grid">

          {/* LEFT SIDE */}

          <div className="query-left">

            <section className="query-card">
              <h3>SEMANTIC INTERPRETATION</h3>

              <div className="interpretation-grid">

                <div className="interpretation-item">
                  <span>PARAMETER</span>
                  <strong>Salinity</strong>
                </div>

                <div className="interpretation-item">
                  <span>REGION</span>
                  <strong>Arabian Sea</strong>
                </div>

                <div className="interpretation-item">
                  <span>PERIOD</span>
                  <strong>Last 6 Months</strong>
                </div>

                <div className="interpretation-item">
                  <span>OPERATION</span>
                  <strong>Comparison</strong>
                </div>

              </div>
            </section>

            <section className="query-card data-scope">
              <h3>DATA SCOPE</h3>

              <div className="scope-row">
                <span>Profiles Processed</span>
                <strong>48</strong>
              </div>

              <div className="scope-row">
                <span>Active Floats</span>
                <strong>12</strong>
              </div>

              <div className="scope-row">
                <span>Confidence Score</span>
                <strong className="confidence">98.4%</strong>
              </div>
            </section>

          </div>

          {/* RIGHT SIDE */}

          <section className="query-card pipeline-card">

            <div className="pipeline-header">
              <h3>PROCESSING PIPELINE</h3>
              <span>Latency: 412 ms</span>
            </div>

            <div className="pipeline">

              <div className="pipeline-step">
                <div className="pipeline-number">1</div>

                <div>
                  <h4>Understand Intent</h4>

                  <p>
                    NLP interpreted the natural-language question and
                    identified the requested oceanographic task.
                  </p>
                </div>
              </div>

              <div className="pipeline-step">
                <div className="pipeline-number">2</div>

                <div>
                  <h4>Identify Parameters & Retrieve Metadata</h4>

                  <p>
                    Detected salinity, Arabian Sea, comparison operation,
                    and the six-month time constraint.
                  </p>
                </div>
              </div>

              <div className="pipeline-step">
                <div className="pipeline-number">3</div>

                <div>
                  <h4>Filter & Retrieve Profiles</h4>

                  <p>
                    Retrieved 48 ARGO profiles matching the selected
                    spatial and temporal constraints.
                  </p>
                </div>
              </div>

              <div className="pipeline-step">
                <div className="pipeline-number">4</div>

                <div>
                  <h4>Analyze & Compare</h4>

                  <p>
                    Calculated comparison statistics across the
                    retrieved salinity measurements.
                  </p>
                </div>
              </div>

              <div className="pipeline-step completed">
                <div className="pipeline-number">✓</div>

                <div>
                  <h4>Generate Visual & Response</h4>

                  <p>
                    Generated the visualization and conversational
                    summary presented to the user.
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