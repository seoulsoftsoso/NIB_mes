# Generated by Django 3.0.6 on 2024-03-12 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprisemaster',
            name='permissions',
            field=models.CharField(max_length=100, null=True, verbose_name='권한'),
        ),
    ]
