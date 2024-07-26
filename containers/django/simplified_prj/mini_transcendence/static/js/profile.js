function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '')
	{
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++)
		{
			const cookie = cookies[i].trim();
			// does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '='))
			{
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function    get_player_online()
{
    let tab_online = [];
    fetch("/api/players/all/online/except-me/", {
		method: 'GET',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		},
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
        data.online_players.forEach(player => {
            tab_online.push(player);
        }); 
	})
	.catch(error => {
        console.log(error);
		alert('Error fetching data:', error);
	});
    console.log(tab_online);
    return (tab_online);
}

function    get_friend_list(url_all)
{
    let tab_online = get_player_online();
    fetch(url_all, {
		method: 'GET',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		},
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {

        data.players.forEach(players => {
            if (players.he_is_my_friend === true){
                let img = document.createElement("img");
                img.src = players.avatar_url;
                img.className = "avatar img-thumbnail rounded-circle";
                img.alt = "friend-avatar";
                tab_online.forEach(online_player => {
                    console.log(online_player);
                    if (players.username == online_player.username){
                        img.style = "width: 100px; height: 100px; border-style: solid; border-color: green; border-width: 3px 3px 3px 3px";
                    }
                    else{
                        img.style = "width: 100px; height: 100px;";
                    }
                });
                let div = document.getElementById("avatar-group");
                div.appendChild(img);
            }
        }); 
	})
	.catch(error => {
        console.log(error);
		alert('Error fetching data:', error);
	});
}

document.addEventListener("DOMContentLoaded", function () {
    get_friend_list("/api/players/all/except-me/");
});