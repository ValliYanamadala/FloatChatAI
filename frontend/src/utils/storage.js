const EXPLORER_KEY = "floatchat_explorer_state";
const ANALYTICS_KEY = "floatchat_analytics_state";

export function saveExplorerState(state) {
  localStorage.setItem(EXPLORER_KEY, JSON.stringify(state));
}

export function getExplorerState() {
  const saved = localStorage.getItem(EXPLORER_KEY);
  if (!saved) return null;
  try {
    return JSON.parse(saved);
  } catch {
    return null;
  }
}

export function clearExplorerState() {
  localStorage.removeItem(EXPLORER_KEY);
}

export function saveAnalyticsState(state) {
  localStorage.setItem(ANALYTICS_KEY, JSON.stringify(state));
}

export function getAnalyticsState() {
  const saved = localStorage.getItem(ANALYTICS_KEY);
  if (!saved) return null;
  try {
    return JSON.parse(saved);
  } catch {
    return null;
  }
}