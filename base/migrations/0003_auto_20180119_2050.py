# Generated by Django 2.0.1 on 2018-01-19 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20180118_1930'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artifacts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupid', models.CharField(max_length=50)),
                ('artifactid', models.CharField(max_length=50)),
                ('version', models.CharField(max_length=50)),
                ('sha1', models.CharField(max_length=40)),
            ],
            options={
                'ordering': ('groupid', 'artifactid', 'version'),
            },
        ),
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detected', models.DateTimeField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='applicationserver',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='repository',
            options={'ordering': ('name',)},
        ),
        migrations.AddField(
            model_name='deployment',
            name='applicationServer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.ApplicationServer'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='artifact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='base.Artifacts'),
        ),
        migrations.AddField(
            model_name='artifacts',
            name='repository',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Repository'),
        ),
    ]