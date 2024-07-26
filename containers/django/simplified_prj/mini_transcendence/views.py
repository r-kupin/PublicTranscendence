from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from .views.auth_views import *
from .views.lobby_views import *
from .views.api_views import *