from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from wellbeing_app.models import MoodEntry, JournalEntry, Affirmation, User
from .forms import MoodEntryForm, JournalEntryForm, AffirmationForm, UserForm

@login_required
def dashboard_home(request):
    # Admin stats
    if request.user.is_staff:
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'mood_entries': MoodEntry.objects.count(),
            'journal_entries': JournalEntry.objects.count(),
        }
    else:
        stats = None
    
    # User-specific data
    context = {
        'stats': stats,
        'recent_moods': MoodEntry.objects.filter(user=request.user).order_by('-date')[:5],
        'recent_journals': JournalEntry.objects.filter(user=request.user).order_by('-date')[:3],
        'todays_affirmation': Affirmation.objects.order_by('?').first(),
    }
    return render(request, 'dashboard/home.html', context)

# Mood Views
@login_required
def mood_list(request):
    moods = MoodEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard/mood/list.html', {'moods': moods})

@login_required
def mood_add(request):
    if request.method == 'POST':
        form = MoodEntryForm(request.POST)
        if form.is_valid():
            mood = form.save(commit=False)
            mood.user = request.user
            mood.save()
            messages.success(request, 'Mood entry added successfully!')
            return redirect('dashboard:mood_list')
    else:
        form = MoodEntryForm()
    return render(request, 'dashboard/mood/add.html', {'form': form})

# Journal Views
@login_required
def journal_list(request):
    journals = JournalEntry.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard/journal/list.html', {'journals': journals})

@login_required
def journal_add(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            journal = form.save(commit=False)
            journal.user = request.user
            journal.save()
            messages.success(request, 'Journal entry added successfully!')
            return redirect('dashboard:journal_list')
    else:
        form = JournalEntryForm()
    return render(request, 'dashboard/journal/add.html', {'form': form})

# Affirmation Views
@login_required
def affirmation_list(request):
    affirmations = Affirmation.objects.all()
    return render(request, 'dashboard/affirmation/list.html', {'affirmations': affirmations})

@login_required
def affirmation_add(request):
    if request.method == 'POST':
        form = AffirmationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Affirmation added successfully!')
            return redirect('dashboard:affirmation_list')
    else:
        form = AffirmationForm()
    return render(request, 'dashboard/affirmation/add.html', {'form': form})

# User Management Views (staff only)
@user_passes_test(lambda u: u.is_staff)
def user_list(request):
    users = User.objects.all()
    return render(request, 'dashboard/user/list.html', {'users': users})

@user_passes_test(lambda u: u.is_staff)
def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User added successfully!')
            return redirect('dashboard:user_list')
    else:
        form = UserForm()
    return render(request, 'dashboard/user/add.html', {'form': form})