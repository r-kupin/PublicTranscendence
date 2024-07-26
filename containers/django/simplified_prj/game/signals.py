from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import GameRecord


@receiver(post_save, sender=GameRecord)
def add_game_record_to_players(sender, instance, created, **kwargs):
    if created:
        instance.player1.records.add(instance)
        instance.player2.records.add(instance)
        if instance.winner:
            if instance.winner.id == instance.player1.id:
                instance.player2.loses += 1
            else:
                instance.player1.loses += 1
            instance.winner.wins += 1
        instance.player1.save()
        instance.player2.save()


@receiver(post_delete, sender=GameRecord)
def remove_game_record_from_players(sender, instance, **kwargs):
    instance.player1.records.remove(instance)
    instance.player2.records.remove(instance)
    if instance.winner:
        if instance.winner.id == instance.player1.id:
            instance.player2.loses -= 1
        else:
            instance.player1.loses -= 1
        instance.winner.wins -= 1
    instance.player1.save()
    instance.player2.save()