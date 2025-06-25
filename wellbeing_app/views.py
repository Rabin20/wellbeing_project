from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _, get_language, activate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import random
import json

from .forms import MoodEntryForm, JournalEntryForm, AffirmationForm
from .models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation

# Home Page
def home(request):
    activate(get_language())
    return render(request, 'home.html')

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activate(get_language())
        return context

# User Registration
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

# Mood Tracking
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
    context['page_title'] = _('Mood Tracker') if get_language() == 'en' else 'Pūrongo Āhua'
    return render(request, 'wellbeing/mood_tracker.html', context)

@login_required
def mood_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
    context = {
        'entries': entries,
        'page_title': _('Mood History') if get_language() == 'en' else 'Hītori Āhua',
        'no_entries': _('No entries submitted yet') if get_language() == 'en' else 'Kāore he pūrongo kua tukuna'
    }
    return render(request, 'wellbeing/mood_history.html', context)

# Journal Views
@login_required
def journal_list(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-date')
    context = {
        'entries': entries,
        'page_title': _('Journal List') if get_language() == 'en' else 'Rārangi Pukapuka',
        'no_entries': _('No journal entries yet') if get_language() == 'en' else 'Kāore he tuhinga kua tuhia'
    }
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
    context['page_title'] = _('Add Journal Entry') if get_language() == 'en' else 'Tāpiri Tuhinga'
    return render(request, 'journal/add.html', context)

# Translation API
@csrf_exempt
def translate_bulk(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texts = data.get('texts', [])
            translations = {
                "I am worthy of love and respect": "He mea nui ahau mō te aroha me te whakaute",
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

# Daily Affirmations
class DailyAffirmationsView(TemplateView):
    template_name = 'affirmations/affirmations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AffirmationForm()
        lang = self.request.LANGUAGE_CODE
        user = self.request.user
        selected_category = self.request.GET.get('category')

        base_qs = Affirmation.objects.filter(
            Q(created_by=user) | Q(created_by__isnull=True),
            active=True,
            language=lang
        )
        if selected_category:
            base_qs = base_qs.filter(category=selected_category)

        context['affirmations'] = list(base_qs.order_by('?')[:6])
        context['selected_category'] = selected_category
        context['categories'] = dict(Affirmation.CATEGORY_CHOICES)

        if user.is_authenticated:
            context['user_affirmations'] = Affirmation.objects.filter(
                created_by=user, active=True, language=lang
            )
            favorite_ids = FavoriteAffirmation.objects.filter(user=user).values_list('affirmation_id', flat=True)
            context['favorites'] = set(favorite_ids)
            context['favorite_affirmations'] = Affirmation.objects.filter(id__in=favorite_ids)
        else:
            context['user_affirmations'] = Affirmation.objects.none()
            context['favorites'] = set()
            context['favorite_affirmations'] = Affirmation.objects.none()

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

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class FavoriteAffirmationsView(ListView):
    template_name = 'affirmations/favorites.html'
    context_object_name = 'favorite_affirmations'

    def get_queryset(self):
        return FavoriteAffirmation.objects.filter(user=self.request.user).select_related('affirmation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = set(
            FavoriteAffirmation.objects.filter(user=self.request.user)
            .values_list('affirmation_id', flat=True)
        )
        return context

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
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})
    except Affirmation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': _('Affirmation not found')}, status=404)

class HelplineView(TemplateView):
    template_name = 'helpline/helpline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helplines'] = [
            {'name': _("Lifeline Aotearoa"), 'number': "0800 543 354", 'description': _("24/7 crisis support")},
            {'name': _("Youthline"), 'number': "0800 376 633", 'description': _("Support for young people")},
            {'name': _("Depression Helpline"), 'number': "0800 111 757", 'description': _("Support for depression and anxiety")}
        ]
        return context

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
