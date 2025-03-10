# Generated by Django 4.2.11 on 2024-06-11 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_transcendence', '0013_remove_player_group_chats'),
        ('chat', '0006_remove_chat_name_chat_created_at_alter_message_chat_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupchat',
            name='players',
            field=models.ManyToManyField(blank=True, related_name='group_chats', to='mini_transcendence.player'),
        ),
    ]
