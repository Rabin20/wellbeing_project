from django import forms
from django.utils.translation import gettext_lazy as _
from .models import MoodEntry, JournalEntry, Affirmation

class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _("Add any notes about your mood..."),
                'rows': 3
            }),
        }

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['description', 'image', 'is_private']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _("Share your thoughts..."),
                'rows': 3
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

class AffirmationForm(forms.ModelForm):
    class Meta:
        model = Affirmation
        fields = ['text', 'language', 'category']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _("Write your positive affirmation..."),
                'rows': 3
            }),
            'language': forms.Select(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }