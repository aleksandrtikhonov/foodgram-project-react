# Generated by Django 4.0.6 on 2022-07-24 16:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_follow_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='self_follow',
        ),
    ]
