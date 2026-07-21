fetch("https://lichess.org/team/the-chess-fan-club/members")
  .then(res => res.text())
  .then(html => {
    console.log(html); // Raw HTML
    document.body.innerHTML = html; // Display it
  });