export default async function handler(req, res) {
    try {
        const response = await fetch(
            "https://lichess.org/team/the-chess-fan-club/members",
            {
                headers: {
                    "User-Agent": "Chess Fan Club Website"
                }
            }
        );

        const html = await response.text();

        res.setHeader("Content-Type", "text/html");
        res.status(200).send(html);

    } catch (err) {
        res.status(500).json({
            error: err.message
        });
    }
}