# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-01 20:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='coursenumber',
            unique_together=set([('subject', 'number')]),
        ),
    ]