document.addEventListener('DOMContentLoaded', function() {
	const playerLinks = document.querySelectorAll('.players-list a');
	const ban_form = document.querySelectorAll('.ban_form form');
	console.log(ban_form);

	playerLinks.forEach(link => {
		link.addEventListener('click', function(event) {
			event.preventDefault(); // prevent default link behavior
			const url = this.href;

			// check if the player information is already displayed
			const playerInfoContainer = document.getElementById('player-info');
			const isDisplayed = playerInfoContainer.dataset.playerId === url;

			if (isDisplayed) {
				// if the same player is clicked again, hide the info
				playerInfoContainer.innerHTML = '';
				playerInfoContainer.removeAttribute('data-player-id');
			} else {
				fetch(url)
				.then(response => {
					if (!response.ok) {
						throw new Error('Network response was not ok');
					}
					return response.json();
				})
				.then(data => {
					displayPlayerData(data.player, url);
				})
				.catch(error => {
					console.error('Error fetching player data:', error);
					alert('Error loading player data.');
				});
			}
		});
	});

	ban_form.forEach(button  => {
		console.log(button.id);
        button.addEventListener('submit', function(event) {
			console.log("ban add event");
            const url = document.getElementById("block-link").value;
            console.log(url);
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                alert("Player banned succesfully.");
            })
            .catch(error => {
                console.error('Error fetching player data:', error);
                alert('Error loading player data.');
            });
        })
    })
});

// NOTE: sometimes need to do a hard refresh (Ctrl + F5) for the css to apply properly
function displayPlayerData(player, url) {
	const playerInfoContainer = document.getElementById('player-info');
	playerInfoContainer.dataset.playerId = url; // Store the URL to identify the player
	
	let addFriendButton = '';
	if (!player.he_is_my_friend) {
		addFriendButton = `<button id="add-friend-button" onclick="addFriend(${player.id})">Add friend</button>`;
	}
	let removeFriendButton = '';
	if (player.he_is_my_friend) {
		removeFriendButton = `<button id="remove-friend-button" onclick="removeFriend(${player.id})">Remove friend</button>`;
	}
	let chatButton = '';
	if (!player.has_dialogue_with_me) {
		chatButton = `<button id="chat-button" onclick="createChat(${player.id})">Create chat</button>`;
	}
	
	if (!player.i_am_blocked && !player.he_is_blocked) {
		playerInfoContainer.innerHTML = `
			<h2>${player.username}</h2>
			<img src="${player.avatar_url}" alt="${player.username}'s avatar">
			<p class="mt-2">Wins: ${player.wins}</p>
			<p>Loses: ${player.loses}</p>
			<div class="friend-list mt-2 text-white">
				<h6 class="text-white">Friends:</h6>
				<ul id="friend-list-content"></ul>
			<button id="invite-button" onclick="inviteUser(${player.id})">Invite to play</button>
			${chatButton}
			${addFriendButton}
			${removeFriendButton}
			<button id="block-button" onclick="blockUser(${player.id})">Block</button>
		`;
		// <p><a href="${player.actions_link}">Actions</a></p>

		// fetch friend list data
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
						console.log('Friend data received:', friendData); // Debug log
						const friendItem = document.createElement('li');
						if (friendData.player.username) {
							friendItem.textContent = friendData.player.username;
						} else {
							friendItem.textContent = 'Unknown friend'; // Default text if username is missing
						}
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
	} else {
		if (player.he_is_blocked && !player.i_am_blocked) {
			playerInfoContainer.innerHTML = `
			<h2>Blocked</h2>
			<button id="unblock-button" onclick="unblockUser(${player.id})">Unblock</button>
		`;
		} else {
			playerInfoContainer.innerHTML = `<h2>Blocked</h2>`;
		}
	}
}

window.addEventListener('pageshow', function(event) {
	if (event.persisted) {
		window.location.reload();
	}
});

function inviteUser(playerId) {
	fetch(`/game/api/match/invite/${playerId}/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('User invited successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error inviting user:', error);
		alert('Error inviting user.');
		location.reload();
	});
}

function createChat(playerId) {
	fetch(`/api/players/${playerId}/create-dialogue/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('Chat created successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error creating chat:', error);
		alert('Error creating chat.');
		location.reload();
	});
}

function addFriend(playerId) {
	fetch(`/api/players/${playerId}/add-friend/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('Friend added successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error sending friend request:', error);
		alert('Error sending friend request.');
		location.reload();
	});
}

function removeFriend(playerId) {
	fetch(`/api/players/${playerId}/remove-friend/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('Friend removed successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error removing friend:', error);
		alert('Error removing friend.');
		location.reload();
	});
}

function blockUser(playerId) {
	fetch(`/api/players/${playerId}/block/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('User blocked successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error blocking user:', error);
		alert('Error blocking user.');
		location.reload();
	});
}

function unblockUser(playerId) {
	fetch(`/api/players/${playerId}/unblock/`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({})
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		console.log('Action success:', data);
		alert('User unblocked successfully!');
		location.reload();
	})
	.catch(error => {
		console.error('Error unblocking user:', error);
		alert('Error unblocking user.');
		location.reload();
	});
}

function deleteChat(delete_url, chatId) {
	fetch(delete_url, {
			method: "POST",
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken')
			},
		}
	)
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		if (data.error) {
			console.error('Error:', data.error);
		} else {
			console.log('Success:', data.message);
			// optionally remove the deleted chat from the DOM
			document.getElementById(`chat_${chatId}`).remove();
		}
	})
	.catch(error => {
		console.error('There was a problem with the fetch operation:', error);
	});
}

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

//	PRESSING ENTER SUBMIT FORM
document.getElementById("message").addEventListener('keypress', function(event) {
	form = document.getElementById("message");
	if (event.key === 'Enter') {
		form.dispatchEvent(new Event('submit')); // dispatch the submit event
	}
});

function	setup_accept_but(button, message)
{
	button.className = "accept-button"
	button.textContent = "Accept";
	button.addEventListener("click", function() {
		// location.href = message.actions.accept_link;
		fetch(message.actions.check_link, {
			method: 'GET',
			headers: {
				'X-CSRFToken': getCookie('csrftoken'),
			}
		})
		.then(response => {
			if (!response.ok) {
				alert("error: This game is not accessible.");
				// throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then(data => {
			if (data.message == 'OK'){
				fetch(message.actions.accept_link, {
                    method: 'POST',
                    headers: {
						'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'),
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => { throw new Error(data.error || 'Error accepting invitation.'); });
                    }
                    return response.text(); // Expecting HTML response
                })
                .then(data => {
					alert("You are about to enter the match... GOOD LUCK!");
                    document.open();
                    document.write(data);
                    document.close();
                })
                .catch(error => {
                    alert(error.message);
                });
			}
		})
	});
}

function	setup_decline_but(button, message, divMessage)
{
	button.className = "decline-button"
	button.textContent = "Decline";
	button.addEventListener("click", function() {
        if (message.invite_confirmed) {
            alert("You have already accepted this invitation. You cannot decline it now.");
            return;
        }
		fetch(message.actions.decline_link, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			}
		})
		.then(response => {
			if (!response.ok) {
				alert("error:This game does not exists.");
			}
			return response.json();
		})
		.then(data => {
			console.log("data.message == ", data.messages);
			let liDecline = document.createElement("li");
			liDecline.textContent = data.message;
			divMessage.appendChild(liDecline); // <=== TODO Newmessage when declined
		})
		.catch(error => {
			alert("error: This game does not exists.", error);
		});
	});
}

function	setup_join_but(button, message)
{
	button.className = "join-button"
	button.addEventListener("click", function() {
		fetch(message.actions.proceed_link, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			}
		})
		.then(response => {
			if (!response.ok)
				return;
			if (response.status == 404)
				return;
			return response.text(); // Expecting HTML response
		})
		.then(data => {
			if (!data.error)
			{
				alert("You are about to enter the match... GOOD LUCK!");
				document.open();
				document.write(data);
				document.close();
			}
			else
				alert(data.error);
		})
		.catch(error => {
			if (error != null)
				alert("catch error: This game does not exists.", error);

		});
	});
}

function	setup_subs_but(formContainer, message, divMessage) {
	formContainer.className = "form-container";
	let aliasForm = document.createElement("form");
	aliasForm.className = "alias-form";

	let aliasInput = document.createElement("input");
	aliasInput.type = "text";
	aliasInput.name = "alias";
	aliasInput.placeholder = "Enter alias";

	let submitButton = document.createElement("button");
	submitButton.type = "submit";
	submitButton.textContent = "Subscribe";

	aliasForm.appendChild(aliasInput);
	aliasForm.appendChild(submitButton);
	formContainer.appendChild(aliasForm);
	divMessage.appendChild(aliasForm);
	aliasForm.addEventListener("submit", function(event) {
		event.preventDefault();
		const alias = aliasInput.value;

		fetch(message.actions.subscribe_link, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': getCookie('csrftoken'),
			},
			body: JSON.stringify({
				'tournament_alias': alias,
			}),
		})
		.then(response => {
			if (!response.ok) {
				alert("Error: Unable to subscribe to the tournament.");
				throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then(data => {
			alert("Successfully subscribed to the tournament!");
		})
		.catch(error => {
			console.error('Error fetching data:', error);
			alert('Error subscribing to the tournament:', error);
		});
	});
}


function display_messages(url) {
	fetch(url, {
		method: 'GET',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		const username = document.getElementById("username").value;
		const chat_id = document.getElementById("chat_id").value;
		let messages_list = document.createElement("ul");
		messages_list.id = "messages_list";
		
		data.messages.forEach(message => {
			let divMessage = document.createElement("div");
			divMessage.className = "message-container";
			let messageContent = document.createElement("div");
			messageContent.className = "message-content";
            let senderName = document.createElement("div"); // Create a new element for the sender's name
            senderName.className = "sender-name";
            senderName.textContent = message.sender_username;
			let liMessage = document.createElement("li");
			liMessage.className = "message-content";
			let buttonContainer = document.createElement("div");
			buttonContainer.className = "button-container";

			// handle invite_received and invite_accepted messages
			if (username == message.sender_username) {
				divMessage.className = "message-container sent";
				messageContent.textContent = message.content;
				divMessage.appendChild(messageContent);
			} else {
				divMessage.className = "message-container received";
				messageContent.textContent = message.content;
                divMessage.appendChild(senderName);
				divMessage.appendChild(messageContent);
			}

			if (message.type === 'invite_received' || message.type === 'invite_accepted'
			|| message.type === 'tournament_match_invite' || message.type === 'tournament_subscription_invite')
			{
				let	but1 = document.createElement("button");
				
				if (message.type === 'invite_received') {
					if (username !== message.sender_username) {
						setup_accept_but(but1, message);

						let but2 = document.createElement("button");
						setup_decline_but(but2, message, divMessage);
						buttonContainer.appendChild(but2);
					}
				} else if (message.type === 'invite_accepted') {
					if (username !== message.sender_username) {
						but1.textContent = "Join";
						setup_join_but(but1, message);
					}
				} else if (message.type === 'tournament_match_invite') {
						but1.textContent = "Join Tournament";
						setup_join_but(but1, message);
				} else if (message.type === 'tournament_subscription_invite') {
					if (username !== message.sender_username) {
						let formContainer = document.createElement("div");
						setup_subs_but(formContainer, message, divMessage);
					}
				}
			if ((username !== message.sender_username && message.type !== 'tournament_subscription_invite') || message.type === 'tournament_match_invite')
				buttonContainer.appendChild(but1);
			divMessage.appendChild(buttonContainer);
		}
		messages_list.append(divMessage);
		});//for Each
		document.getElementById("messages").innerHTML = "";
		document.getElementById("messages").appendChild(messages_list);

		scrollBottom();

	}) //then
	.catch(error => {
		console.error('Error fetching data:', error);
		const contentElement = document.getElementById('messages');
		contentElement.innerHTML = 'Error loading content.';
	});
}

	
function scrollBottom() {
	var divmess = document.getElementById("messages");
	divmess.scrollTop = divmess.scrollHeight;
}

function	display_room_name(url)
{
	fetch(url, {
		method: 'GET',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		let room_name = document.getElementById("room_name");
		room_name.innerHTML = data.chat.name;
	})
	.catch(error => {
		console.error('Error fetching data:', error);
		const contentElement = document.getElementById('room_name');
		contentElement.innerHTML = 'Error loading content.';
	});
}

function	load_room_selection()
{
	forms = document.getElementsByClassName("send_form");

	for (var i = 0; i < forms.length; i++){
		
		forms[i].addEventListener("submit", function(event) {
			event.preventDefault();
			document.getElementById("message").type = ""
			document.getElementById("send_button").removeAttribute("hidden");
			var url = this.action;
			console.log("url messages == ", url);	
			display_messages(url);

			document.getElementById("message-form").action = url + "send/";

			event.preventDefault();
			const chat_id = this.querySelector("#chat_id").value
			url = this.action.slice(0
				, this.action.indexOf(chat_id, this.action.indexOf('/', 8))) + "my/" + chat_id;
			display_room_name(url);
		});
	}
}

document.addEventListener('DOMContentLoaded', function() {
	const socket = new WebSocket(`wss://${window.location.host}/wss/chat/`);
	
	socket.addEventListener('message', function (ev) {
		const data = JSON.parse(ev.data);
		console.log(data)
		// 1. find out what chat is on the screen right now
		// 2. If data['chat_id']:
		display_messages('api/' + data['chat_id'] + '/messages/');
		url = 'api/my/' + data['chat_id'];
		console.log("notif url room == ", url);	
		display_room_name(url);
		
		socket.send(JSON.stringify({
			'type': 'messages_checked',
			'chat_id': data['chat_id'],
			'seen_messages': data['amount_total']
		}))
		document.getElementById("message").value = "";
		// 3. else - show data['amount_unseen'] at the appropriate chat thumbnail
	});
	
	load_room_selection();
	scrollBottom();
	
});

// To send a message //
document.getElementById("message-form").addEventListener("submit", function(event) {
	event.preventDefault();
	const url = this.action;
	const formData = new FormData(this);
	const n_message = document.getElementById("message").value;
	
	fetch(url, {
		method: 'POST',
		body: n_message,
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		}
	})
	.then(response => {
		if (!response.ok) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
		//	DISPLAY MESSAGES
		let divMessage = document.createElement("div");
		let liMessage = document.createElement("li");
		liMessage.textContent = n_message;
		
		divMessage.appendChild(liMessage);
		document.getElementById("messages").appendChild(divMessage);
		
		document.getElementById("message").value = "";
	})
	.catch(error => {
		console.error('Error fetching data:', error);
		const contentElement = document.getElementById('messages');
		contentElement.innerHTML = 'Error loading content.';
	});
});
