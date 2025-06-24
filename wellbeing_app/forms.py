from django import forms
from .models import MoodEntry,JournalEntry, Affirmation


class MoodEntryForm(forms.ModelForm):
    class Meta:
        model = MoodEntry
        fields = ['mood', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add any notes about your mood...'}),
        }

class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['mood', 'title', 'content', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Write about your thoughts, feelings, or anything on your mind...'
            }),
            'tags': forms.TextInput(attrs={
                'placeholder': 'whānau, stress, school, culture'
            })
        }
class AffirmationForm(forms.ModelForm):
    class Meta:
        model = Affirmation
        fields = ['text', 'category']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'})
        }