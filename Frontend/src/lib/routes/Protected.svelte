<script lang="ts">
    import { onMount } from "svelte";
    import keycloak from "../keycloak";

    let username = "";
    let email = "";
    let message = "";
    let isAdmin = false; // Flag to track if user has admin role
    let textFieldValue = "";

    // Fetch user info from backend and check roles
    async function fetchProtectedData() {
        try {
            console.log("Keycloak token:", keycloak.token);

            await keycloak.updateToken(30);

            const res = await fetch("http://127.0.0.1:8000/protected", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${keycloak.token}`,
                },
            });

            if (!res.ok) throw new Error(await res.text());

            const data = await res.json();
            username = data.preferred_username;
            email = data.email;
            message = "Protected data fetched successfully!";

            // Check if the user has 'admin' role
            const tokenParsed = keycloak.tokenParsed as any;
            isAdmin =
                tokenParsed.resource_access["myclient"].roles.includes(
                    "admin",
                ) ?? false;
        } catch (err) {
            message = "Failed to fetch protected data: " + err.message;
            console.error(err);
        }
    }

    function logout() {
        keycloak.logout({ redirectUri: window.location.origin });
    }

    onMount(() => {
        fetchProtectedData();
    });
</script>

<div class="max-w-md mx-auto mt-20 p-6 bg-white shadow-lg rounded-lg">
    <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold">Welcome Back</h2>
        <button
            on:click={logout}
            class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
        >
            Logout
        </button>
    </div>

    {#if username}
        <p class="text-gray-700">Username: {username}</p>
        <p class="text-gray-500 mb-4">Email: {email}</p>

        <!-- Role-based text field -->
        <input
            type="text"
            bind:value={textFieldValue}
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring"
            placeholder="Only admin can edit"
            disabled={!isAdmin}
        />

        {#if !isAdmin}
            <p class="text-sm text-gray-500 mt-1">
                You need admin role to edit this field
            </p>
        {/if}
    {:else}
        <p class="text-red-500">{message}</p>
    {/if}
</div>
