# Generated by Django 4.2.11 on 2024-06-23 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mini_transcendence', '0016_delete_tournament'),
        ('game', '0002_tournament'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_pending', models.BooleanField(default=True)),
                ('link', models.URLField()),
                ('initiator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='initiated_games', to='mini_transcendence.player')),
                ('invited', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accepted_games', to='mini_transcendence.player')),
            ],
        ),
    ]
