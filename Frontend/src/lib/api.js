import keycloak from "./keycloak.js";

export async function fetchProtectedData() {
  // Fetches protected resources from the backend using Keycloak authentication.
  const response = await fetch("http://localhost:8000/protected", {
    headers: {
      Authorization: `Bearer ${keycloak.token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch protected data");
  }

  return response.json();
}
