document.addEventListener("DOMContentLoaded", () => {
    // Relative path pointing to your python backend json storage file
    const jsonSource = "Fetch/Fetch.json";
    
    // DOM Element hooks
    const upcomingBox = document.getElementById("upcoming-list");

    fetch(jsonSource)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP Error Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            // === RENDER UPCOMING MATCHES ===
            upcomingBox.innerHTML = "";
            const futureMatches = data.upcoming_tournaments || [];
            
            if (futureMatches.length === 0) {
                upcomingBox.innerHTML = '<div class="loading-state">No upcoming team battles scheduled at the moment. Check back soon!</div>';
            } else {
                futureMatches.forEach(match => {
                    // Create clean display string from the Lichess timestamp
                    const matchTime = match.startsAt ? new Date(match.startsAt).toLocaleString() : "TBD";
                    
                    upcomingBox.insertAdjacentHTML("beforeend", `
                        <a href="${match.link}" target="_blank" class="match-card">
                            <div class="match-name">${match.fullName}</div>
                            <div class="match-meta">📅 Starts: ${matchTime}</div>
                        </a>
                    `);
                });
            }
        })
        .catch(error => {
            console.error("Upcoming page population failed:", error);
            upcomingBox.innerHTML = '<div class="loading-state" style="color:#ef4444;">❌ Error loading the events schedule.</div>';
        });
});
