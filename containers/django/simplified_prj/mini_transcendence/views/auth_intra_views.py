from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from ..models import Player
from ..utils.oauth2 import *


def intra_callback(request):
    temp_code = request.GET.get('code')
    state = request.GET.get('state')
    if not temp_code or not state:
        print("Intra auth service provided no code or state")
        return redirect('error_page')
    data, token = data_from_intra_by_temp_code(temp_code, state)
    if not data:
        print("Intra auth service provided no data")
        return redirect('error_page')
    if state == "bind":
        return update_data_from_intra(request, data, token, '/settings')
    if state == "upd_image":
        return update_data_from_intra(request, data, token, '/set-image-from-intra')
    elif state == "sign_in":
        return sign_in_with_data_from_intra(request, data, token)
    elif state == "sign_up":
        return sign_up_with_data_from_intra(request, data, token)
    else:
        print("unexpected state")
        return redirect('error_page')


@login_required
def bind_intra(request):
    return initiate_oauth("bind")


def sign_in_intra(request):
    return initiate_oauth("sign_in")


def sign_up_intra(request):
    return initiate_oauth("sign_up")


@login_required
def set_image_from_intra(request):
    player = request.user.player
    if player.intra_token is None:
        print("user isn't bound to intra login")
        return initiate_oauth("upd_image")
    data = data_from_intra_by_token(player)
    if data is None:
        print("asking for a new token")
        return initiate_oauth("upd_image")
    update_avatar_from_intra(data, player)
    return redirect('/settings')


def sign_in_with_data_from_intra(request, data, token):
    intra_login = data['login']

    player = Player.objects.filter(intra_login=intra_login).first()
    if not player:
        print(f"Player associated with intra login \"{intra_login}\" not found")
        user = User.objects.filter(username=intra_login).first()
        if not user:
            return sign_up_with_data_from_intra(request, data, token)
        else:
            print("Found User with matching username."
                  "Please, login without intra auth and connect Intra account in Settings")
            print("Redirecting to login")
            return redirect('/accounts/login')
    user = player.user
    player.intra_token = token
    player.save()
    if user is not None:
        login(request, user)
        return redirect('/home')
    else:
        return HttpResponse("Authentication failed.", status=401)


def update_data_from_intra(request, data, token, redirect_to):
    player = request.user.player
    player.intra_login = data['login']
    player.intra_token = token
    print('token updated')
    player.save()
    return redirect(redirect_to)


def sign_up_with_data_from_intra(request, data, token):
    User.objects.create(
        username=data['login'],
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    player = User.objects.filter(username=data['login']).first().player
    player.intra_token = token
    player.intra_login = data['login']
    update_avatar_from_intra(data, player)
    login(request, player.user)
    return redirect('/home')


def update_avatar_from_intra(data, player):
    image = data['image']['link']
    response = requests.get(image, stream=True)
    if response.status_code == 200:
        # Create a temporary file
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        # Get the field
        field = getattr(player, 'avatar')
        # Set the image field to the downloaded image
        field.save(f'{image.split("/")[-1]}', File(img_temp), save=False)
        # Save the model instance
        player.save()
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
