# Generated by Django 2.0.1 on 2018-01-26 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_deployment_runtimename'),
    ]

    operations = [
        migrations.AddField(
            model_name='artifact',
            name='extension',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
    ]