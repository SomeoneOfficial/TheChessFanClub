console.log(
"The Chess Fan Club website loaded!"
);


class SiteNav extends HTMLElement {
connectedCallback() {
this.innerHTML = `
<nav>
	<div class="logo">♟️ The Chess Fan Club</div>
	<div class="nav-links">
		<a href="index.html">Home</a>
		<a href="tournaments.html">Tournaments</a>
		<a href="hall-of-fame.html">Hall of Fame</a>
		<a href="leaderboard.html">Leaderboard</a>
		<a href="rewards.html">Rewards</a>
		<a href="LichessExtension.html">Lichess Extension</a>
	</div>
</nav>`;
}
}

customElements.define("site-nav", SiteNav);


// Simple animation on cards

const cards =
document.querySelectorAll(".card, .stat-card");


cards.forEach(card => {

card.addEventListener(
"mouseenter",
()=>{

card.style.transition =
"0.3s";

}
);

});