from django.contrib import admin
from .models import *

admin.site.register(GameRecord)
admin.site.register(TournamentRecord)
admin.site.register(TournamentPlayerStat)

# Register your models here.
