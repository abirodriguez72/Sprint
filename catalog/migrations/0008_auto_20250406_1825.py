from django.db import migrations

def set_unique_username(apps, schema_editor):
    User = apps.get_model('catalog', 'User')
    for user in User.objects.all():
        # If the username is the default (or empty), update it with a unique value.
        if not user.username or user.username == 'defaultuser':
            user.username = f"user_{user.user_id}"
            user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_alter_user_username'),  # replace with the last migration file
    ]

    operations = [
        migrations.RunPython(set_unique_username),
    ]
