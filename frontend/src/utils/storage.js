const STORAGE_KEY = "floatchat_explorer_state";

export function saveExplorerState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function getExplorerState() {
  const saved = localStorage.getItem(STORAGE_KEY);

  if (!saved) {
    return null;
  }

  try {
    return JSON.parse(saved);
  } catch {
    return null;
  }
}

export function clearExplorerState() {
  localStorage.removeItem(STORAGE_KEY);
}