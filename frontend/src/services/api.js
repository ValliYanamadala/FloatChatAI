/**
 * FloatChatAI Frontend API Abstraction Service
 * Connects frontend pages to FastAPI backend endpoints via relative /api paths.
 */

const RAW_BASE = import.meta.env.VITE_API_BASE_URL || "";
const API_BASE = RAW_BASE.replace(/\/api\/v1\/?$/, "");

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const timeoutMs = options.timeout || 15000;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData?.detail) {
          errorMessage = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        const text = await response.text();
        if (text) errorMessage = text;
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") {
      throw new Error("Request timed out. Please check backend connection.");
    }
    throw err;
  }
}

/**
 * List ARGO floats with pagination and optional filters.
 */
export async function getFloats(params = {}) {
  const query = new URLSearchParams();
  if (params.page) query.append("page", params.page);
  if (params.page_size) query.append("page_size", params.page_size);
  if (params.status) query.append("status", params.status);

  const qs = query.toString();
  return request(`/api/v1/floats${qs ? `?${qs}` : ""}`);
}

/**
 * Retrieve metadata for a specific ARGO float.
 */
export async function getFloatDetails(floatId) {
  if (!floatId) throw new Error("Float ID is required");
  return request(`/api/v1/floats/${encodeURIComponent(floatId)}`);
}

/**
 * Retrieve chronological trajectory fixes for a specific float.
 */
export async function getFloatTrajectory(floatId) {
  if (!floatId) throw new Error("Float ID is required");
  return request(`/api/v1/floats/${encodeURIComponent(floatId)}/trajectory`);
}

/**
 * List ARGO profiles filterable by float_id and cycle.
 */
export async function getProfiles(params = {}) {
  const query = new URLSearchParams();
  if (params.float_id) query.append("float_id", params.float_id);
  if (params.cycle_number !== undefined) query.append("cycle_number", params.cycle_number);
  if (params.page) query.append("page", params.page);
  if (params.page_size) query.append("page_size", params.page_size);

  const qs = query.toString();
  return request(`/api/v1/profiles${qs ? `?${qs}` : ""}`);
}

/**
 * Retrieve details for a single profile cycle.
 */
export async function getProfile(profileId) {
  if (!profileId) throw new Error("Profile ID is required");
  return request(`/api/v1/profiles/${encodeURIComponent(profileId)}`);
}

/**
 * Query vertical depth slice sensor measurements.
 */
export async function getMeasurements(params = {}) {
  const query = new URLSearchParams();
  if (params.profile_id) query.append("profile_id", params.profile_id);
  if (params.min_depth !== undefined) query.append("min_depth", params.min_depth);
  if (params.max_depth !== undefined) query.append("max_depth", params.max_depth);
  if (params.page) query.append("page", params.page);
  if (params.page_size) query.append("page_size", params.page_size);

  const qs = query.toString();
  return request(`/api/v1/measurements${qs ? `?${qs}` : ""}`);
}

/**
 * Retrieve aggregated statistics across geographic bounding box.
 */
export async function getStatistics(params = {}) {
  const query = new URLSearchParams();
  if (params.min_lat !== undefined) query.append("min_lat", params.min_lat);
  if (params.max_lat !== undefined) query.append("max_lat", params.max_lat);
  if (params.min_lon !== undefined) query.append("min_lon", params.min_lon);
  if (params.max_lon !== undefined) query.append("max_lon", params.max_lon);

  const qs = query.toString();
  return request(`/api/v1/statistics${qs ? `?${qs}` : ""}`);
}

/**
 * PostGIS geodesic proximity radius search.
 */
export async function getNearestFloats(payload) {
  return request("/api/v1/nearest-floats", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/**
 * Send natural language question to the multi-criteria AI query engine.
 */
export async function sendAIQuery(question) {
  return request("/api/v1/query", {
    method: "POST",
    body: JSON.stringify({
      natural_language_prompt: question,
    }),
  });
}

/**
 * Health check endpoint.
 */
export async function getHealth() {
  return request("/api/v1/health");
}