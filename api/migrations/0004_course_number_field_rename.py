# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-30 18:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_offering_add_primary_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='num',
            new_name='number',
        ),
        migrations.RenameField(
            model_name='coursenumber',
            old_name='num',
            new_name='number',
        ),
    ]