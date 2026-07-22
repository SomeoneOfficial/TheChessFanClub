document.addEventListener("DOMContentLoaded", () => {
    // Correct target path pointing to your edited python storage file
    const jsonSource = "Fetch/Fetch.json";
    
    // DOM Element hooks
    const joinersBox = document.getElementById("joiners-list");

    fetch(jsonSource)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            // === RENDER RECENT JOINERS ===
            joinersBox.innerHTML = "";
            const members = data.recent_joiners || [];
            
            if (members.length === 0) {
                joinersBox.innerHTML = '<div class="loading-state">No recent members listed.</div>';
            } else {
                members.forEach(member => {
                    // Prefer a username field if present, fall back to id
                    const userId = member.username || member.id || "Unknown";
                    const safeId = encodeURIComponent(userId);

                    // Link to lichess profile at /@/username and show the userId text
                    joinersBox.insertAdjacentHTML("beforeend", `
                        <a href="https://lichess.org/@/${safeId}" target="_blank" rel="noopener" class="joiner-link">
                            <div class="joiner-tag">
                                <span class="joiner-icon">●</span>
                                <span class="joiner-id">${userId}</span>
                            </div>
                        </a>
                    `);
                });
            }
        })
        .catch(error => {
            console.error("Dashboard population failed:", error);
            const alertMsg = '<div class="loading-state" style="color:#ef4444;">❌ Error loading data source.</div>';
            joinersBox.innerHTML = alertMsg;
        });
});
