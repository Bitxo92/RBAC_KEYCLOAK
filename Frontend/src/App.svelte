<script lang="ts">
  import { onMount } from "svelte";
  import Protected from "./lib/routes/Protected.svelte";
  import keycloak from "./lib/keycloak";
  import { fetchProtectedData } from "./lib/api";

  // Flags for tracking initialization and authentication status
  let initialized = false;
  let authenticated = false;

  // Initialize Keycloak on component mount
  onMount(async () => {
    try {
      const ok = await keycloak.init({ onLoad: "login-required" });
      console.log("Init result:", ok, "Authenticated:", keycloak.authenticated);

      // Update state after successful init
      initialized = true;
      authenticated = keycloak.authenticated;

      // Fetch protected data only if authenticated
      if (authenticated) {
        await fetchProtectedData();
      }
    } catch (err) {
      console.error("Keycloak init failed", err);
      initialized = true;
      authenticated = false;
    }
  });
</script>

{#if !initialized}
  <p class="text-gray-500 text-center mt-10">Initializing Keycloak...</p>
{:else if authenticated && keycloak.token}
  <Protected />
{:else}
  <p class="text-red-500 text-center mt-10">User not authenticated</p>
{/if}
