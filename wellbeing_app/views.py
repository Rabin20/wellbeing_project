from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import MoodEntryForm, JournalEntryForm
from .models import MoodEntry, JournalEntry
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils.translation import get_language, activate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils.translation import BulkTranslator  # Import our translation utility
from django.shortcuts import render

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if get_language() == 'mi':
            context.update({
                'welcome': "Nau mai ki te Taupānga Hauora",
                'page_title': 'Hauora Hapori',
                'content': {
                    'heading': 'Te tautoko i te hauora hinengaro mō ngā taiohi Māori me ngā taiohi ahurea maha',
                    'description': 'Tō paetukutuku mō te tautoko hauora hinengaro me ngā rauemi hapori.'
                }
            })
        else:
            context.update({
                'welcome': "Welcome to Wellbeing App",
                'page_title': 'Community Wellbeing',
                'content': {
                    'heading': 'Supporting Mental Health for Māori and Multicultural Youth',
                    'description': 'Your platform for community mental health support and resources.'
                }
            })
        return context

# Translation API Views
@csrf_exempt
def translate_bulk(request):
    """Handle bulk translation requests from the client"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texts = data.get('texts', [])
            target_lang = data.get('target_lang', 'mi')
            
            translator = BulkTranslator()
            translations = translator.translate_bulk(texts, target_lang)
            
            return JsonResponse({'translations': translations})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def set_language_ajax(request):
    """Handle language preference changes via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            language = data.get('language', 'en')
            activate(language)  # Activate the language immediately
            request.session['django_language'] = language
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid request'}, status=400)

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
@login_required
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
    
    # Add translation context
    context = {'form': form}
    if get_language() == 'mi':
        context['page_title'] = 'Pūrongo Āhua'
    else:
        context['page_title'] = 'Mood Tracker'
    
    return render(request, 'wellbeing/mood_tracker.html', context)

@login_required
def mood_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
    
    # Add translation context
    context = {'entries': entries}
    if get_language() == 'mi':
        context.update({
            'page_title': 'Hītori Āhua',
            'no_entries': 'Kāore he pūrongo kua tukuna'
        })
    else:
        context.update({
            'page_title': 'Mood History',
            'no_entries': 'No entries submitted yet'
        })
    
    return render(request, 'wellbeing/mood_history.html', context)

# Journal Views
@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    
    # Add translation context
    context = {'entries': entries}
    if get_language() == 'mi':
        context.update({
            'page_title': 'Rārangi Pukapuka',
            'no_entries': 'Kāore he tuhinga kua tuhia'
        })
    else:
        context.update({
            'page_title': 'Journal List',
            'no_entries': 'No journal entries yet'
        })
    
    return render(request, 'journal/list.html', context)

@login_required
def journal_add(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('journal_list')
    else:
        form = JournalEntryForm()
    
    # Add translation context
    context = {'form': form}
    if get_language() == 'mi':
        context['page_title'] = 'Tāpiri Tuhinga'
    else:
        context['page_title'] = 'Add Journal Entry'
    
    return render(request, 'journal/add.html', context)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)