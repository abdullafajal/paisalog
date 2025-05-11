from django.db import migrations

def create_missing_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('core', 'UserProfile')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_userprofile_is_salaried_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles),
    ] 