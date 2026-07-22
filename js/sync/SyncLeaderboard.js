document.addEventListener("DOMContentLoaded", () => {
    // Relative path targeting the JSON created by your python backend
    const jsonPath = "Fetch/Fetch.json";
    const tilesContainer = document.getElementById("leaderboard-tiles");

    fetch(jsonPath)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP network error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Clear out loading status message
            tilesContainer.innerHTML = "";

            const leaderboard = data.player_leaderboard;
            const entries = Object.entries(leaderboard);

            if (entries.length === 0) {
                tilesContainer.innerHTML = '<div class="loading-state">No finished tournament history found.</div>';
                return;
            }

            // Loop through ordered JSON items and assemble individual tiles
            entries.forEach(([username, score], index) => {
                const rank = index + 1;
                
                // Establish styling classes based on leader placement
                let rankClass = "";
                if (rank === 1) rankClass = "rank-1";
                else if (rank === 2) rankClass = "rank-2";
                else if (rank === 3) rankClass = "rank-3";

                tilesContainer.addEventListener("mouseover", () => {
                    tilesContainer.style.cursor = "pointer";
                });

                const tileHtml = `
                    <div class="player-tile ${rankClass}" data-username="${username}">
                        <div class="player-info">
                            <span class="player-rank">${rank}</span>
                            <span class="player-name">${username}</span>
                        </div>
                        <div class="player-score">
                            ${score} pts
                        </div>
                    </div>
                `;
                
                tilesContainer.insertAdjacentHTML("beforeend", tileHtml);
            });

            tilesContainer.addEventListener("click", (event) => {
                const tile = event.target.closest(".player-tile");
                if (!tile) return;

                const username = tile.dataset.username;
                if (username) {
                    window.NewWindow = window.open("https://lichess.org/@/" + username, "_blank");
                }
            });
        })
        .catch(error => {
            console.error("Error loading the leaderboard file:", error);
            tilesContainer.innerHTML = `
                <div class="error-state">
                    ❌ Failed to render tournament leaderboard. Ensure script has run successfully.
                </div>
            `;
        });
});
