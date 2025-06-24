from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class MoodEntry(models.Model):
    MOOD_CHOICES = [
        ('happy', _('😊 Happy/Pai')),
        ('calm', _('😌 Calm/Noho pai')),
        ('neutral', _('😐 Neutral/Haupapa')),
        ('anxious', _('😟 Anxious/Māharahara')),
        ('angry', _('😠 Angry/Riri')),
        ('sad', _('😢 Sad/Pōuri')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, verbose_name=_('mood'))
    notes = models.TextField(blank=True, verbose_name=_('notes'))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_('date'))
    
    class Meta:
        verbose_name = _('Mood Entry')
        verbose_name_plural = _('Mood Entries')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_mood_display()} - {self.date.strftime('%Y-%m-%d')}"

class Affirmation(models.Model):
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('mi', _('Māori'))
    ]
    
    CATEGORY_CHOICES = [
        ('self_esteem', _('Self-Esteem')),
        ('strength', _('Strength')),
        ('culture', _('Cultural Identity')),
        ('community', _('Community')),
    ]
    
    text = models.CharField(max_length=200, verbose_name=_('affirmation text'))
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_('language'))
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='self_esteem', verbose_name=_('category'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('created at'))
    active = models.BooleanField(default=True, verbose_name=_('active'))
    
    # User relationship fields
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_affirmations',
        verbose_name=_('created by')
    )
    is_user_generated = models.BooleanField(
        default=False,
        verbose_name=_('user generated')
    )
    favorited_by = models.ManyToManyField(
        User,
        through='FavoriteAffirmation',
        related_name='favorite_affirmations',
        verbose_name=_('favorited by')
    )

    class Meta:
        verbose_name = _('Affirmation')
        verbose_name_plural = _('Affirmations')
        ordering = ['language', 'category']
        indexes = [
            models.Index(fields=['language', 'active']),
            models.Index(fields=['created_by', 'is_user_generated']),
        ]
    
    def __str__(self):
        return f"{self.text[:50]}... ({self.get_language_display()})"
    
    def is_favorite_of(self, user):
        """Check if this affirmation is favorited by a specific user"""
        if not user.is_authenticated:
            return False
        return self.favorited_by.filter(pk=user.pk).exists()

class FavoriteAffirmation(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='affirmation_favorites',
        verbose_name=_('user')
    )
    affirmation = models.ForeignKey(
        Affirmation,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name=_('affirmation')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('favorited at')
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('personal notes'),
        help_text=_('Add personal notes about why this affirmation is meaningful to you')
    )

    class Meta:
        unique_together = ('user', 'affirmation')
        verbose_name = _('Favorite Affirmation')
        verbose_name_plural = _('Favorite Affirmations')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s favorite: {self.affirmation.text[:30]}..."

class JournalEntry(models.Model):
    MOOD_CHOICES = MoodEntry.MOOD_CHOICES  # Reuse the same choices
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='journal_entries',
        verbose_name=_('user')
    )
    date = models.DateTimeField(
        default=timezone.now, 
        verbose_name=_('date')
    )
    mood = models.CharField(
        max_length=20, 
        choices=MOOD_CHOICES, 
        verbose_name=_('mood')
    )
    title = models.CharField(
        max_length=100, 
        verbose_name=_('title')
    )
    content = models.TextField(verbose_name=_('content'))
    tags = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name=_('tags'),
        help_text=_("Comma-separated tags like 'whānau,stress,school'")
    )
    is_private = models.BooleanField(
        default=True,
        verbose_name=_('private entry'),
        help_text=_('Keep this entry visible only to you')
    )
    related_affirmations = models.ManyToManyField(
        Affirmation,
        blank=True,
        related_name='journal_entries',
        verbose_name=_('related affirmations'),
        help_text=_('Affirmations that might relate to this journal entry')
    )

    class Meta:
        verbose_name = _('Journal Entry')
        verbose_name_plural = _('Journal Entries')
        ordering = ['-date']
        permissions = [
            ('view_community_journal', _('Can view community journal entries'))
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.title} ({self.date.strftime('%Y-%m-%d')})"

    def get_tags(self):
        """Returns a list of cleaned tags"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('journal_detail', kwargs={'pk': self.pk})