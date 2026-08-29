const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const text = await response.text();

    throw new Error(
      text || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export function getFloats(params = {}) {
  const query = new URLSearchParams(params).toString();

  return request(
    `/api/v1/floats${query ? `?${query}` : ""}`
  );
}

export function getFloatDetails(floatId) {
  return request(`/api/v1/floats/${floatId}`);
}

export function getFloatTrajectory(floatId) {
  return request(`/api/v1/floats/${floatId}/trajectory`);
}

export function getProfile(profileId) {
  return request(`/api/v1/profiles/${profileId}`);
}

export function getMeasurements(params = {}) {
  const query = new URLSearchParams(params).toString();

  return request(
    `/api/v1/measurements${query ? `?${query}` : ""}`
  );
}

export function getStatistics(params = {}) {
  const query = new URLSearchParams(params).toString();

  return request(
    `/api/v1/statistics${query ? `?${query}` : ""}`
  );
}

export function getNearestFloats(payload) {
  return request("/api/v1/nearest-floats", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function sendAIQuery(question) {
  return request("/api/v1/query", {
    method: "POST",
    body: JSON.stringify({
      query: question,
    }),
  });
}

export function getHealth() {
  return request("/api/v1/health");
}