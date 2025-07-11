from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _, get_language, activate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
import json
import random

from .forms import MoodEntryForm, JournalEntryForm, AffirmationForm
from .models import MoodEntry, JournalEntry, Affirmation, FavoriteAffirmation

# ---------------- HOME ----------------
@login_required
def home(request):
    activate(get_language())
    journal_entries = []

    if request.method == 'POST' and 'journal_submit' in request.POST:
        journal_form = JournalEntryForm(request.POST, request.FILES)
        if journal_form.is_valid():
            entry = journal_form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('home')
    else:
        journal_form = JournalEntryForm()

    journal_entries = JournalEntry.objects.filter(
        Q(is_private=False) | Q(user=request.user)
    ).order_by('-date')

    for entry in journal_entries:
        entry.reaction_counts = entry.get_reaction_counts()
        entry.user_reaction = entry.get_user_reaction(request.user)

    context = {
        'journal_entries': journal_entries,
        'journal_form': journal_form,
    }
    return render(request, 'home.html', context)

# ---------------- REGISTER ----------------
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

# ---------------- MOOD TRACKER ----------------
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
    return render(request, 'mood/mood_tracker.html', context)

@login_required
def mood_history(request):
    entries = MoodEntry.objects.filter(user=request.user).order_by('-date')
    context = {
        'entries': entries,
        'page_title': _('Mood History') if get_language() == 'en' else 'Hītori Āhua',
        'no_entries': _('No entries submitted yet') if get_language() == 'en' else 'Kāore he pūrongo kua tukuna'
    }
    return render(request, 'mood/mood_history.html', context)

# ---------------- JOURNAL ENTRIES ----------------
@login_required
def journal_list(request):
    filter_type = request.GET.get('filter', 'my')

    if filter_type == 'my':
        entries = JournalEntry.objects.filter(user=request.user)
    elif filter_type == 'public':
        entries = JournalEntry.objects.filter(is_private=False).exclude(user=request.user)
    elif filter_type == 'all':
        if request.user.is_staff:
            entries = JournalEntry.objects.all().order_by('-date')
        else:
            entries = JournalEntry.objects.filter(
                Q(is_private=False) | Q(user=request.user)
            ).order_by('-date')
    else:
        entries = JournalEntry.objects.none()

    entries = entries.order_by('-date')
    return render(request, 'journal/list.html', {
        'journal_entries': entries,
        'filter_type': filter_type,
    })

@login_required
def journal_add(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('home')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = JournalEntryForm()

    return render(request, 'journal/add.html', {
        'form': form,
        'page_title': _('Add Journal Entry') if get_language() == 'en' else 'Tāpiri Tuhinga'
    })

@login_required
def journal_edit(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = JournalEntryForm(instance=entry)
    return render(request, 'journal/edit.html', {'form': form})

@login_required
def journal_delete(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('home')
    return render(request, 'journal/confirm_delete.html', {'object': entry})

@require_POST
@login_required
def react_to_journal(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    reaction = request.POST.get('reaction')
    current_reaction = entry.get_user_reaction(request.user)
    
    if current_reaction == reaction:
        entry.remove_reaction(request.user)
    else:
        entry.add_reaction(request.user, reaction)

    return JsonResponse({
        'status': 'success',
        'counts': entry.get_reaction_counts(),
        'user_reaction': entry.get_user_reaction(request.user)
    })

@require_POST
@login_required
def upload_journal_image(request):
    if 'image' not in request.FILES:
        return JsonResponse({'error': _('No image provided')}, status=400)

    image = request.FILES['image']
    if image.size > 5 * 1024 * 1024:
        return JsonResponse({'error': _('Image too large (max 5MB)')}, status=400)

    return JsonResponse({'success': True, 'url': '/media/temp/' + image.name})

# ---------------- AFFIRMATIONS ----------------
class DailyAffirmationsView(TemplateView):
    template_name = 'affirmations/affirmations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context.update({
            'form': AffirmationForm(),
            'affirmations': list(base_qs.order_by('?')[:6]),
            'selected_category': selected_category,
            'categories': dict(Affirmation.CATEGORY_CHOICES),
            'user_affirmations': Affirmation.objects.filter(created_by=user, active=True, language=lang),
            'favorites': set(FavoriteAffirmation.objects.filter(user=user).values_list('affirmation_id', flat=True)),
            'favorite_affirmations': Affirmation.objects.filter(id__in=FavoriteAffirmation.objects.filter(user=user).values_list('affirmation_id', flat=True)),
        })
        return context

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

def staff_check(user):
    return user.is_staff

@user_passes_test(staff_check)
@login_required
def affirmation_edit(request, pk):
    affirmation = get_object_or_404(Affirmation, pk=pk)
    if request.method == 'POST':
        form = AffirmationForm(request.POST, instance=affirmation)
        if form.is_valid():
            form.save()
            messages.success(request, _('Affirmation updated successfully!'))
            return redirect('affirmations')
    else:
        form = AffirmationForm(instance=affirmation)
    return render(request, 'affirmations/edit_affirmation.html', {'form': form})

@user_passes_test(staff_check)
@login_required
def affirmation_delete(request, pk):
    affirmation = get_object_or_404(Affirmation, pk=pk)
    if request.method == 'POST':
        affirmation.delete()
        messages.success(request, _('Affirmation deleted.'))
        return redirect('affirmations')
    return render(request, 'affirmations/confirm_delete.html', {'object': affirmation})

@method_decorator(login_required, name='dispatch')
class FavoriteAffirmationsView(ListView):
    template_name = 'affirmations/favorites.html'
    context_object_name = 'favorite_affirmations'

    def get_queryset(self):
        return FavoriteAffirmation.objects.filter(user=self.request.user).select_related('affirmation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['favorites'] = set(
            FavoriteAffirmation.objects.filter(user=self.request.user).values_list('affirmation_id', flat=True)
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

# ---------------- MOOD CRUD ----------------
@login_required
def mood_edit(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MoodEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('mood_history')
    else:
        form = MoodEntryForm(instance=entry)
    return render(request, 'mood/edit.html', {'form': form})

@login_required
def mood_delete(request, pk):
    entry = get_object_or_404(MoodEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        return redirect('mood_history')
    return render(request, 'mood/confirm_delete.html', {'object': entry})
# ---------------- HELPLINE ----------------
class HelplineView(TemplateView):
    template_name = 'helpline/helpline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['helplines'] = [
            {'name': _("Lifeline Aotearoa"), 'number': "0800 543 354", 'description': _("24/7 crisis support")},
            {'name': _("Youthline"), 'number': "0800 376 633", 'description': _("Support for young people")},
            {'name': _("Depression Helpline"), 'number': "0800 111 757", 'description': _("Support for depression and anxiety")},
        ]
        return context
# ---------------- ERROR PAGES ----------------
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
