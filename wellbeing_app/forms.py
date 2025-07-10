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
                'placeholder': _("What's on your mind?"),
                'rows': 3,
                'required': True
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(_("Image too large (max 5MB)"))
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError(_("File is not an image"))
        return image

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