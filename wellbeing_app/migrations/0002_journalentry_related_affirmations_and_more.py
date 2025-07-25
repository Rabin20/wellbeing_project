# Generated by Django 5.2.3 on 2025-06-24 01:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellbeing_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='related_affirmations',
            field=models.ManyToManyField(blank=True, help_text='Affirmations that might relate to this journal entry', to='wellbeing_app.affirmation', verbose_name='related affirmations'),
        ),
        migrations.CreateModel(
            name='FavoriteAffirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saved_at', models.DateTimeField(auto_now_add=True, verbose_name='saved at')),
                ('notes', models.TextField(blank=True, verbose_name='personal notes')),
                ('affirmation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wellbeing_app.affirmation', verbose_name='affirmation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Favorite Affirmation',
                'verbose_name_plural': 'Favorite Affirmations',
                'ordering': ['-saved_at'],
                'unique_together': {('user', 'affirmation')},
            },
        ),
    ]
