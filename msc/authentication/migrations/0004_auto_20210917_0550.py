# Generated by Django 3.1.2 on 2021-09-17 05:50

from django.db import migrations


def create_staff_groups(apps, schema_editor):

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    # Create groups
    admin = Group.objects.create(name="Admin")
    super_admin = Group.objects.create(name="SuperAdmin")



    admin_perm_models = {
        "authentication": {
            "user": ["add", "view", "change", "delete"]
        },
        "questionnaire": {
            "questionnaire": ["view"],
            "question": ["view"],
            "section": ["view"],
            "questionlogic": ["view"]
        },
        "response": {
            "response": ["view"],
            "questionresponse": ["view"]
        }

    }

    super_admin_perm_models = {
        "authentication": {
            "user": ["add", "view", "change", "delete"]
        },
        "questionnaire": {
            "questionnaire": ["add", "view", "change", "delete"],
            "question": ["add", "view", "change", "delete"],
            "section": ["add", "view", "change", "delete"],
            "questionlogic": ["add", "view", "change", "delete"]
        },
        "organisation": {
            "organisation": ["add", "view", "change", "delete"],
            "group": ["add", "view", "change", "delete"],
        },
        "response": {
            "response": ["view"],
            "questionresponse": ["view"]
        }
    }

    # Assign perms to groups
    for app_label, models in admin_perm_models.items():
        for model, perms in models.items():
            for perm in perms:
                permission = Permission.objects.filter(
                    content_type__app_label=app_label, codename=f"{perm}_{model}"
                ).first()
                admin.permissions.add(permission)


    for app_label, models in super_admin_perm_models.items():
        for model, perms in models.items():
            for perm in perms:
                permission = Permission.objects.filter(
                    content_type__app_label=app_label, codename=f"{perm}_{model}"
                ).first()
                super_admin.permissions.add(permission)


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_remove_user_is_admin'),
    ]

    operations = [
        migrations.RunPython(create_staff_groups),
    ]
