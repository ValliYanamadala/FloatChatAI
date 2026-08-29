import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">🌊</div>

        <div>
          <h2>FloatChat AI</h2>
          <p>OCEAN INTELLIGENCE</p>
        </div>
      </div>

      <button className="new-analysis">
        + New Analysis
      </button>

      <nav className="nav-menu">
        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          Home
        </NavLink>

        <NavLink
          to="/explorer"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          Explorer
        </NavLink>

        <NavLink
          to="/float/2901234"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          Float Details
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          Analytics
        </NavLink>

        <NavLink
          to="/query-explanation"
          className={({ isActive }) =>
            isActive ? "nav-item active" : "nav-item"
          }
        >
          Query Explanation
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <p>◉ Argo Status</p>
        <p>▣ System Logs</p>
      </div>
    </aside>
  );
}

export default Sidebar;