# Generated by Django 2.1.5 on 2019-01-08 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(max_length=500)),
                ('is_open', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(editable=False)),
            ],
        ),
    ]
