# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0003_category_slugs'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='slugs',
            new_name='slug',
        ),
    ]
