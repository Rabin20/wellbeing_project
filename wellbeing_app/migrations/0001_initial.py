# Generated by Django 5.2.3 on 2025-06-18 04:39

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Affirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, verbose_name='affirmation text')),
                ('language', models.CharField(choices=[('en', 'English'), ('mi', 'Māori')], max_length=2, verbose_name='language')),
                ('category', models.CharField(choices=[('self_esteem', 'Self-Esteem'), ('strength', 'Strength'), ('culture', 'Cultural Identity'), ('community', 'Community')], default='self_esteem', max_length=20, verbose_name='category')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('active', models.BooleanField(default=True, verbose_name='active')),
            ],
            options={
                'verbose_name': 'Affirmation',
                'verbose_name_plural': 'Affirmations',
                'ordering': ['language', 'category'],
            },
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date')),
                ('mood', models.CharField(choices=[('happy', '😊 Happy/Pai'), ('calm', '😌 Calm/Noho pai'), ('neutral', '😐 Neutral/Haupapa'), ('anxious', '😟 Anxious/Māharahara'), ('angry', '😠 Angry/Riri'), ('sad', '😢 Sad/Pōuri')], max_length=20, verbose_name='mood')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('tags', models.CharField(blank=True, help_text="Comma-separated tags like 'whānau,stress,school'", max_length=200, verbose_name='tags')),
                ('is_private', models.BooleanField(default=True, help_text='Keep this entry visible only to you', verbose_name='private entry')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Journal Entry',
                'verbose_name_plural': 'Journal Entries',
                'ordering': ['-date'],
                'permissions': [('view_community_journal', 'Can view community journal entries')],
            },
        ),
        migrations.CreateModel(
            name='MoodEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mood', models.CharField(choices=[('happy', '😊 Happy/Pai'), ('calm', '😌 Calm/Noho pai'), ('neutral', '😐 Neutral/Haupapa'), ('anxious', '😟 Anxious/Māharahara'), ('angry', '😠 Angry/Riri'), ('sad', '😢 Sad/Pōuri')], max_length=20, verbose_name='mood')),
                ('notes', models.TextField(blank=True, verbose_name='notes')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Mood Entry',
                'verbose_name_plural': 'Mood Entries',
                'ordering': ['-date'],
            },
        ),
    ]
