from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import MoodEntryForm
from .models import MoodEntry
from .models import JournalEntry
from .forms import JournalEntryForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.translation import get_language


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if get_language() == 'mi':
            context['welcome'] = "Nau mai ki te Taupānga Hauora"
        else:
            context['welcome'] = "Welcome to Wellbeing App"
        return context
    
    
# Authentication Views
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('mood_tracker')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Mood Tracking Views
def mood_tracker(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('mood_history')
    else:
        form = MoodEntryForm()
    return render(request, 'wellbeing/mood_tracker.html', {'form': form})

def mood_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'wellbeing/mood_history.html', {'entries': entries})

def home(request):
    # Add any context data you want to pass to the template
    context = {
        'page_title': 'Community Wellbeing',
        'content': {
            'heading': 'Supporting Mental Health for Māori and Multicultural Youth',
            'description': 'Your platform for community mental health support and resources.'
        }
    }
    return render(request, 'home.html', context)


@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'journal/list.html', {'entries': entries})

@login_required
def journal_add(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user  # Set the user before saving
            entry.save()
            return redirect('journal_list')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add.html', {'form': form})