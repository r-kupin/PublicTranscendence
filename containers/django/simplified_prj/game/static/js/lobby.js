function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '')
	{
		const cookies = document.cookie.split(';');
        console.log("cookies: ". cookies);
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

function getFormattedTimestamp() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
	let hours = String(now.getHours()).padStart(2, '0');
	let minutes = String(now.getMinutes() + 2).padStart(2, '0');
	if (minutes > 59) {
		minutes -= 60;
		hours += 1;
	}
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const milliseconds = String(now.getMilliseconds()).padStart(3, '0');
    
    return year + "-" + month + "-" + day + "T" + hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}

// 2024-07-12T12:02:23.317
// 2024-07-18T18:49:18.340

function    create_tournament(url)
{
    fetch(url, {
		method: 'POST',
		headers: {
			'X-CSRFToken': getCookie('csrftoken'),
		},
        body: JSON.stringify({
            'starts_at': getFormattedTimestamp(),
        }),
	})
	.then(response => {
		if (!response.ok && response.status != 400) {
			throw new Error('Network response was not ok');
		}
		return response.json();
	})
	.then(data => {
        if (data.status == 400)
            console.log(data.status);
        alert("Creating a tournament group chat")
        window.location.href = '/chat';
	})
	.catch(error => {
        console.log(error);
		alert('Error fetching data:', error);
	});
}

document.getElementById("create_form").addEventListener("submit", function(event) {
    event.preventDefault();
    create_tournament(document.getElementById("create_form").action);
});
