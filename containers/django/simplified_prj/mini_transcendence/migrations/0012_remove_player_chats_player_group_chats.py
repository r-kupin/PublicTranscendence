# Generated by Django 4.2.11 on 2024-06-11 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_remove_chat_name_chat_created_at_alter_message_chat_and_more'),
        ('mini_transcendence', '0011_remove_player_rooms_player_chats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='chats',
        ),
        migrations.AddField(
            model_name='player',
            name='group_chats',
            field=models.ManyToManyField(blank=True, related_name='players', to='chat.groupchat'),
        ),
    ]
