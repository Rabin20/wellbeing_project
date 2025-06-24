from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import MoodEntryForm, JournalEntryForm, AffirmationForm
from .models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView
from django.utils.translation import get_language, activate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.contrib import messages

def home(request):
    activate(get_language())
    return render(request, 'home.html')

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activate(get_language())
        return context

# Translation Views
@csrf_exempt
def translate_bulk(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texts = data.get('texts', [])
            target_lang = data.get('target_lang', 'mi')
            
            # Simple translation dictionary (replace with your actual translation logic)
            translations = {
                "I am worthy of love and respect": "He mea nui ahau mō te aroha me te whakaute",
                # Add more translations as needed
            }
            
            translated = [translations.get(text, text) for text in texts]
            return JsonResponse({'translations': translated})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def set_language_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            language = data.get('language', 'en')
            activate(language)
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
    
    context = {'form': form}
    if get_language() == 'mi':
        context['page_title'] = 'Pūrongo Āhua'
    else:
        context['page_title'] = 'Mood Tracker'
    
    return render(request, 'wellbeing/mood_tracker.html', context)
# Journal Views
@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    
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
    
    context = {'form': form}
    if get_language() == 'mi':
        context['page_title'] = 'Tāpiri Tuhinga'
    else:
        context['page_title'] = 'Add Journal Entry'
    
    return render(request, 'journal/add.html', context)
@login_required
def mood_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
    context = {
        'entries': entries,
        'page_title': 'Mood History',
        'no_entries': 'No entries submitted yet'
    }
    
    if get_language() == 'mi':
        context.update({
            'page_title': 'Hītori Āhua',
            'no_entries': 'Kāore he pūrongo kua tukuna'
        })
    
    return render(request, 'wellbeing/mood_history.html', context)

# Affirmations Views
class DailyAffirmationsView(TemplateView):
    template_name = 'affirmations/affirmations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AffirmationForm()
        current_language = self.request.LANGUAGE_CODE
        
        # Get all active affirmations in current language
        all_affirmations = list(Affirmation.objects.filter(
            active=True,
            language=current_language
        ))
        
        # If no affirmations exist, create some defaults
        if not all_affirmations:
            all_affirmations = self.create_default_affirmations(current_language)
        
        # Select 6 random affirmations
        context['affirmations'] = random.sample(all_affirmations, min(6, len(all_affirmations)))
            
        return context
    
    def create_default_affirmations(self, language):
        defaults = {
            'en': [
                "I am worthy of love and respect",
                "I am capable of achieving my goals",
                "My challenges help me grow",
                "I choose to focus on what I can control",
                "I am enough just as I am",
                "I welcome positivity into my life"
            ],
            'mi': [
                "He mea nui ahau mō te aroha me te whakaute",
                "Ka taea e au te tutuki i aku whāinga",
                "Ko aku wero e āwhina ana i ahau ki te tipu",
                "Ka arohia e au ngā mea ka taea e au te whakahaere",
                "He pai rawa atu ahau",
                "Ka whakatau ahau i te pai ki toku oranga"
            ]
        }
        
        created = []
        for text in defaults.get(language, []):
            aff, _ = Affirmation.objects.get_or_create(
                text=text,
                language=language,
                defaults={'category': 'self_esteem', 'active': True}
            )
            created.append(aff)
        
        return created
    
    def post(self, request, *args, **kwargs):
        form = AffirmationForm(request.POST)
        if form.is_valid():
            affirmation = form.save(commit=False)
            affirmation.language = request.LANGUAGE_CODE
            if request.user.is_authenticated:
                affirmation.created_by = request.user
                affirmation.is_user_generated = True
            affirmation.active = True
            affirmation.save()
            messages.success(request, _('Affirmation added successfully!'))
            return redirect('affirmations')
        
        # If form is invalid, show errors
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class FavoriteAffirmationsView(ListView):
    template_name = 'affirmations/favorites.html'
    model = FavoriteAffirmation
    context_object_name = 'favorites'
    
    def get_queryset(self):
        return FavoriteAffirmation.objects.filter(user=self.request.user).select_related('affirmation')

@require_POST
@login_required
def save_affirmation(request):
    affirmation_id = request.POST.get('affirmation_id')
    if not affirmation_id:
        return JsonResponse({'status': 'error'}, status=400)
    
    try:
        affirmation = Affirmation.objects.get(id=affirmation_id)
        fav, created = FavoriteAffirmation.objects.get_or_create(
            user=request.user,
            affirmation=affirmation
        )
        return JsonResponse({
            'status': 'added' if created else 'already_exists',
            'message': _('Saved to favorites!') if created else _('Already in favorites')
        })
    except Affirmation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Affirmation not found')}, status=400)

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
# @login_required  
# class MoodHistoryView(ListView):
#     template_name = 'wellbeing/mood_history.html'
#     model = MoodEntry
#     context_object_name = 'entries'

#     def get_queryset(self):
#         if self.request.user.is_authenticated:
#             return MoodEntry.objects.filter(user=self.request.user).order_by('-date')
#         return MoodEntry.objects.none()

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if get_language() == 'mi':
#             context.update({
#                 'page_title': 'Hītori Āhua',
#                 'no_entries': 'Kāore he pūrongo kua tukuna'
#             })
#         else:
#             context.update({
#                 'page_title': 'Mood History',
#                 'no_entries': 'No entries submitted yet'
#             })
#         return context

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)