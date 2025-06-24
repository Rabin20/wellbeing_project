from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import MoodEntryForm, JournalEntryForm
from .models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.utils.translation import get_language, activate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from .utils.translation import BulkTranslator  # Import our translation utility
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST


def home(request):
    # Activate the current language
    activate(get_language())
    return render(request, 'home.html')

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activate(get_language())  # Ensure the correct language is activate
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

class DailyAffirmationsView(TemplateView):
    template_name = 'affirmations/affirmations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_language = self.request.LANGUAGE_CODE
        affirmations = Affirmation.objects.filter(
            active=True,
            language=current_language   
        )
        if affirmations.count() >= 6:
            context['affirmations'] = random.sample(list(affirmations), 6)
        else:
            # Fallback to a predefined list if not enough affirmations
            context['affirmations'] = affirmations
        return context
@login_required
@require_POST
def save_favorite(request):
    affirmation_text = request.POST.get('affirmation')
    if not affirmation_text:
        return JsonResponse({'status': 'error'}, status=400)
    
    # Get or create the affirmation
    affirmation, created = Affirmation.objects.get_or_create(text=affirmation_text)
    
    # Add to favorites if not already
    fav, created = FavoriteAffirmation.objects.get_or_create(
        user=request.user,
        affirmation=affirmation
    )
    
    return JsonResponse({'status': 'added' if created else 'already_exists'})

@login_required
def favorite_affirmations(request):
    favorites = FavoriteAffirmation.objects.filter(user=request.user)
    return render(request, 'affirmations/favorites.html', {'favorites': favorites})

class MoodHistoryView(ListView):
    template_name = 'mood_history/mood_history.html'
    model = MoodEntry
    context_object_name = 'entries'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return MoodEntry.objects.filter(user=self.request.user).order_by('-date')
        return MoodEntry.objects.none()

class HelplineView(TemplateView):
    template_name = 'helpline/helpline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helplines'] = [
            {
                'name': _("Lifeline Aotearoa"),
                'number': "0800 543 354",
                'description': _("24/7 crisis support")
            },
            {
                'name': _("Youthline"),
                'number': "0800 376 633",
                'description': _("Support for young people")
            },
            {
                'name': _("Depression Helpline"),
                'number': "0800 111 757",
                'description': _("Support for depression and anxiety")
            }
        ]
        return context


def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)