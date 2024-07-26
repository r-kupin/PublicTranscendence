from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import quote, urlencode
import requests


def initiate_oauth(state):
    query_params = urlencode({
        'client_id': settings.OAUTH2_CLIENT_ID,
        'redirect_uri': settings.INTRA_REDIRECT_LINK,
        'response_type': 'code',
        'state': state
    })
    oauth_url = f'{settings.OAUTH2_AUTH_URL}?{query_params}'
    return HttpResponseRedirect(oauth_url)


def get_intra_token(temp_code, state):
    query_params = urlencode({
        'grant_type': 'authorization_code',
        'client_id': settings.OAUTH2_CLIENT_ID,
        'client_secret': settings.OAUTH2_CLIENT_SECRET,
        'code': temp_code,
        'redirect_uri': settings.INTRA_REDIRECT_LINK,
        'state': state
    })
    oauth_url = f'{settings.OAUTH2_TOKEN_URL}?{query_params}'
    response = requests.post(oauth_url)
    return response.json().get('access_token')


def data_from_intra_by_temp_code(temp_code, state):
    token = get_intra_token(temp_code, state)
    if not token:
        print("Intra auth service provided no token")
        return redirect('error_page')
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(settings.OAUTH2_MY_DATA_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data, token


def data_from_intra_by_token(player):
    headers = {
        'Authorization': f'Bearer {player.intra_token}'
    }
    response = requests.get(settings.OAUTH2_TOKEN_INFO_URL, headers=headers)
    if not response.ok:
        print("Bad token")
        return None

    data = response.json()
    if not data:
        print("Intra auth service provided no data")
        return redirect('error_page')
    token_valid_untill = data['expires_in_seconds']
    if token_valid_untill < 0:
        print("Token expired")
        return None
    response = requests.get(settings.OAUTH2_MY_DATA_URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data
