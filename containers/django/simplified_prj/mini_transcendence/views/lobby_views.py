from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib.auth.decorators import login_required

from ..forms import UserForm, PlayerForm
from ..models import Player


@login_required
def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))


@login_required
def profile(request):
    template = loader.get_template('profile.html')
    player = request.user.player
    avg_score = player.avg_score()
    context = {
        'player': player,
        'avg_score': "{:.2f}".format(avg_score),
    }
    return HttpResponse(template.render(context, request))


@login_required
def stats(request):
    template = loader.get_template('stats.html')
    player = Player.objects.get(user=request.user)
    winrate = 0
    if player.records.count() != 0:
        winrate = player.wins / player.records.count() * 100
    avg_score = player.avg_score()
    context = {
        'player': player,
        'games': player.records.all(),
        'winrate': "{:.1f}".format(winrate),
        'avg_score': "{:.2f}".format(avg_score),
    }
    return HttpResponse(template.render(context, request))


@login_required
def settings(request):
    player = request.user.player

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        player_form = PlayerForm(request.POST, request.FILES, instance=player)
        if user_form.is_valid() and player_form.is_valid():
            user_form.save()
            player_form.save()
            return redirect('settings')  # Redirect to the settings page after form submission
    else:
        user_form = UserForm(instance=request.user)
        player_form = PlayerForm(instance=player)

    context = {
        'player': player,
        'user_form': user_form,
        'player_form': player_form,
    }
    return render(request, 'settings.html', context)
