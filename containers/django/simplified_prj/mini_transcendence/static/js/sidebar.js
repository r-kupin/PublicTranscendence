// // DOM est une représentation hiérarchique de la page web, où chaque élément HTML est un objet qu'on peut manipuler de manière dynamique
// // e.g. on peut modifier la structure, le style et le contenu
document.addEventListener('DOMContentLoaded', function() {
    const onlineUsersList = document.getElementById("online-users-list");
    const playerDataModal = new bootstrap.Modal(document.getElementById('playerDataModal'));
    const playerDataContent = document.getElementById('player-data-content');
    const playerDataModalLabel = document.getElementById('playerDataModalLabel');

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // CSRF token
    const csrftoken = getCookie('csrftoken');

    // Fetch online users
    fetch('/api/players/all/online/except-me/')
        .then(response => response.json())
        .then(data => {
            onlineUsersList.innerHTML = '';
            data['online_players'].forEach(user => {
                if (user['i_am_blocked']) {
                    return;
                }
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.textContent = user['username'];
                a.href = "#";
                a.dataset.userId = user['id'];
                a.dataset.userName = user['username'];
                a.className = 'sidebar-link';
                if (user['he_is_blocked']) {
                    a.addEventListener('click', unblockUser);
                } else {
                    a.addEventListener('click', handleUserClick);
                }
                li.appendChild(a);
                onlineUsersList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error loading dynamic content:', error);
        });

    function handleUserClick(event) {
        event.preventDefault();
        const userId = event.target.dataset.userId;
        const userName = event.target.dataset.userName;

        playerDataModalLabel.textContent = userName;
        
        fetch(`/api/players/${userId}/actions/`)
            .then(response => response.json())
            .then(data => {
                playerDataContent.innerHTML = '';
                for (const [actionName, actionLink] of Object.entries(data.actions)) {
                    const actionItem = document.createElement('div');
                    const button = document.createElement('button');
                    button.className = 'btn btn-primary mt-2 action-link';
                    button.dataset.action = actionLink;
                    button.dataset.actionName = actionName;
                    switch (actionName) {
                        case 'get_player_data':
                            button.textContent = 'Profile';
                            break;
                        case 'add_to_friendlist':
                            button.textContent = 'Add friend';
                            break;
                        case 'remove_from_friendlist':
                            button.textContent = 'Remove friend';
                            break;
                        case 'create_dialogue':
                            button.textContent = 'Create chat';
                            break;
                        case 'remove_dialogue':
                            button.textContent = 'Remove chat';
                            break;
                        case 'goto_dialogue':
                            button.textContent = 'Send message';
                            break;
                        case 'block_player':
                            button.textContent = 'Block';
                            break;
                        case 'invite_for_match':
                            button.textContent = 'Invite to play';
                            break;
                        default:
                            button.textContent = actionName;
                    }
                    actionItem.appendChild(button);
                    playerDataContent.appendChild(actionItem);
                }
                playerDataModal.show();
                document.querySelectorAll('.action-link').forEach(link => {
                    link.addEventListener('click', handleActionClick);
                });
            })
            .catch(error => {
                console.error('Error fetching user actions:', error);
            });
    }

    function handleActionClick(event) {
        event.preventDefault();
        const actionLink = event.target.getAttribute('data-action');
        const actionName = event.target.getAttribute('data-action-name');
        
        if (actionLink.includes('/api/players/me/')) {
            fetch(actionLink)
                .then(response => response.json())
                .then(data => {
                    const player = data.player;
                    const playerDataHtml = `
                        <div class="player-profile">
                            <img src="${player.avatar_url}" alt="${sanitizeHTML(player.username)}'s avatar" class="avatar">
                            <p>Wins: ${sanitizeHTML(player.wins.toString())}</p>
                            <p>Loses: ${sanitizeHTML(player.loses.toString())}</p>
                        </div>
                        <div class="friend-list mt-2 text-white">
                            <h6 class="text-white">Friends:</h6>
                            <ul id="friend-list-content"></ul>
                        </div>
                        <div class="recent-matches mt-2 text-white">
                            <h6 class="text-white">Recent Matches:</h6>
                            <table class="table table-dark table-striped" id="recent-matches-content">
                                <thead>
                                    <tr>
                                        <th>Match ID</th>
                                        <th>Winner</th>
                                        <th>Score</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    `;
                    playerDataContent.innerHTML = playerDataHtml;

                    const friendListContent = document.getElementById('friend-list-content');
                    if (player.friendlist.length === 0) {
                        const noFriendsItem = document.createElement('li');
                        noFriendsItem.textContent = 'No friends found';
                        friendListContent.appendChild(noFriendsItem);
                    } else {
                        player.friendlist.forEach(friendUrl => {
                            fetch(friendUrl)
                                .then(response => response.json())
                                .then(friendData => {
                                    const friendItem = document.createElement('li');
                                    friendItem.textContent = sanitizeHTML(friendData.player.username || 'Unknown friend');
                                    friendListContent.appendChild(friendItem);
                                })
                                .catch(error => {
                                    console.error('Error fetching friend data:', error);
                                    const errorItem = document.createElement('li');
                                    errorItem.textContent = 'Error loading friend';
                                    friendListContent.appendChild(errorItem);
                                });
                        });
                    }

                    const recentMatchesContent = document.querySelector('#recent-matches-content tbody');
                    if (player.records.length === 0) {
                        const noMatchesRow = document.createElement('tr');
                        noMatchesRow.innerHTML = '<td colspan="3">No matches found</td>';
                        recentMatchesContent.appendChild(noMatchesRow);
                    } else {
                        player.records.forEach(recordUrl => {
                            fetch(recordUrl)
                                .then(response => response.json())
                                .then(recordData => {
                                    const recordRow = document.createElement('tr');
                                    recordRow.innerHTML = `
                                        <td>${sanitizeHTML(recordData.record.id.toString())}</td>
                                        <td>${sanitizeHTML(recordData.record.winner)}</td>
                                        <td>${sanitizeHTML(recordData.record.player1_score.toString())} - ${sanitizeHTML(recordData.record.player2_score.toString())}</td>
                                        <td>${new Date(recordData.record.timestamp).toLocaleDateString()}</td>
                                    `;
                                    recentMatchesContent.appendChild(recordRow);
                                })
                                .catch(error => {
                                    console.error('Error fetching record data:', error);
                                    const errorRow = document.createElement('tr');
                                    errorRow.innerHTML = '<td colspan="3">Error loading match</td>';
                                    recentMatchesContent.appendChild(errorRow);
                                });
                        });
                    }
                })
                .catch(error => {
                    console.error('Error fetching player data:', error);
                });
        } else {
            fetch(actionLink, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (['create_dialogue', 'remove_dialogue', 'goto_dialogue', 'invite_for_match'].includes(actionName)) {
                    window.location.href = '/chat';
                } else {
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error with action request:', error);
                alert(`Action error: ${error}`);
                location.reload();
            });
        }
    }

    function unblockUser(event) {
        event.preventDefault();
        const userId = event.target.dataset.userId;
        const userName = event.target.dataset.userName;

        playerDataModalLabel.textContent = userName;
        
        fetch(`/api/players/${userId}/actions/`)
            .then(response => response.json())
            .then(data => {
                playerDataContent.innerHTML = '';
                for (const [actionName, actionLink] of Object.entries(data.actions)) {
                    const actionItem = document.createElement('div');
                    if (actionName === 'unblock_player') {
                        const button = document.createElement('button');
                        button.className = 'btn btn-primary mt-2 action-link';
                        button.dataset.action = actionLink;
                        button.dataset.actionName = actionName;
                        button.textContent = 'Unblock';
                        actionItem.appendChild(button);
                    }
                    playerDataContent.appendChild(actionItem);
                }
                playerDataModal.show();
                document.querySelectorAll('.action-link').forEach(link => {
                    link.addEventListener('click', handleActionClick);
                });
            })
            .catch(error => {
                console.error('Error fetching user actions:', error);
            });
    }

    // Sidebar toggle functionality
    const toggleBtn = document.getElementById("toggle-btn");
    toggleBtn.addEventListener("click", function() {
        document.querySelector("#sidebar").classList.toggle("expand");
    });

    // Hide online users list initially if sidebar is expanded
    const sidebar = document.querySelector("#sidebar");
    if (sidebar.classList.contains("expand")) {
        onlineUsersList.style.display = 'none';
    }

    // Close the online users list when clicking outside the sidebar
    document.addEventListener('click', function(event) {
        if (!sidebar.contains(event.target) && onlineUsersList.style.display === 'block') {
            onlineUsersList.style.display = 'none';
        }
    });

    // Toggle the online users list when clicking on its toggle button
    const onlineUsersToggle = document.getElementById('online-users-toggle');
    onlineUsersToggle.addEventListener('click', function(event) {
        event.preventDefault();
        onlineUsersList.style.display = onlineUsersList.style.display === 'block' ? 'none' : 'block';
    });

    // Utility function to sanitize HTML
    function sanitizeHTML(str) {
        const temp = document.createElement('div');
        temp.textContent = str;
        return temp.innerHTML;
    }
});
