# Generated by Django 2.1.5 on 2019-01-08 14:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('threads', '0012_auto_20190108_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
