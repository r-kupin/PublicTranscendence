function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const avgScoreElement = document.getElementById('avgScore');
    const avgScoreBar = document.getElementById('avgScoreBar');
    const tournamentStatsElement = document.getElementById('tournamentStats');

    // Update average score bar width
    if (avgScoreElement && avgScoreBar) {
        const avgScore = parseFloat(avgScoreElement.textContent);
        const percentage = (avgScore / 5) * 100;
        avgScoreBar.style.width = percentage + '%';
    }

    // Fetch player data
    if (tournamentStatsElement) {
        fetch('/api/players/me/')
            .then(response => response.json())
            .then(data => {
                const player = data.player;
                if (player.tournament_stats.length === 0) {
                    const noTournament = document.createElement('li');
                    noTournament.textContent = 'No participated tournament';
                    tournamentStatsElement.appendChild(noTournament);
                } else {
                    let first = 0;
                    let second = 0;
                    const fetchPromises = player.tournament_stats.map(tournamentUrl => {
                        return fetch(tournamentUrl, {
                            method: 'GET',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                            }
                        })
                        .then(response => {
                            if (!response.ok) {
                                alert("error");
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.player_tournament_record.rank === 1) {
                                first++;
                            } else if (data.player_tournament_record.rank === 2) {
                                second++;
                            }
                        });
                    });

                    Promise.all(fetchPromises).then(() => {
                        const rank1 = document.createElement('h2');
                        const rank2 = document.createElement('h2');
                        rank1.className = "col";
                        rank2.className = "col";
                        rank1.innerHTML = `1st Place: ${first}`;
                        rank2.innerHTML = `2nd Place: ${second}`;
                        tournamentStatsElement.appendChild(rank1);
                        tournamentStatsElement.appendChild(rank2);
                    }).catch(error => console.error('Error fetching tournament data:', error));
                }
            })
            .catch(error => console.error('Error fetching player data:', error));
    }
});
