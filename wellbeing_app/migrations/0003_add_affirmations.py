from django.db import migrations
from django.utils.translation import gettext_lazy as _

def add_affirmations(apps, schema_editor):
    Affirmation = apps.get_model('wellbeing_app', 'Affirmation')
    
    english_affirmations = [
        ("I am worthy of love and respect", "self_esteem"),
        ("I am capable of achieving my goals", "strength"),
        ("My challenges help me grow", "strength"),
        ("I choose to focus on what I can control", "self_esteem"),
        ("I am enough just as I am", "self_esteem"),
        ("I welcome positivity into my life", "community"),
        ("My Māori heritage makes me strong", "culture"),
        ("I honor my ancestors with my actions", "culture"),
        ("I contribute positively to my community", "community"),
        ("I trust in my ability to handle challenges", "strength")
    ]
    
    maori_affirmations = [
        ("He mea nui ahau mō te aroha me te whakaute", "self_esteem"),
        ("Ka taea e au te tutuki i aku whāinga", "strength"),
        ("Ko aku wero e āwhina ana i ahau ki te tipu", "strength"),
        ("Ka arohia e au ngā mea ka taea e au te whakahaere", "self_esteem"),
        ("He pai rawa atu ahau", "self_esteem"),
        ("Ka whakatau ahau i te pai ki toku oranga", "community"),
        ("Ko toku tuakiri Māori he mea kaha moku", "culture"),
        ("Ka whakahōnoretia e au ōku tīpuna mā aku mahi", "culture"),
        ("Ka whai wāhi atu ahau ki te hapori", "community"),
        ("Ka whakapono ahau ki toku āheinga ki te whakatutuki i nga wero", "strength")
    ]
    
    # Add English affirmations
    for text, category in english_affirmations:
        Affirmation.objects.get_or_create(
            text=text,
            language='en',
            category=category
        )
    
    # Add Māori affirmations
    for text, category in maori_affirmations:
        Affirmation.objects.get_or_create(
            text=text,
            language='mi',
            category=category
        )

class Migration(migrations.Migration):
    dependencies = [
        ('wellbeing_app', '0001_initial'),  # Replace with your actual last migration
    ]
    
    operations = [
        migrations.RunPython(add_affirmations),
    ]