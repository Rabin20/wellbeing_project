from django import forms
from django.utils.translation import gettext_lazy as _
from .models import MoodEntry, JournalEntry, Affirmation
from django.core.files.uploadedfile import UploadedFile

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

    if image and isinstance(image, UploadedFile):
        # Only do content_type check for new uploads
        if image.size > 5 * 1024 * 1024:  # Limit size to 5MB
            raise forms.ValidationError(_('Image file too large (max 5MB).'))

        if image.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
            raise forms.ValidationError(_('Invalid image format. Please upload JPG, PNG, or GIF.'))

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