# Generated by Django 2.0 on 2018-01-26 19:50

from django.db import migrations, models
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0030_auto_20180120_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='requested_launch',
            field=models.DateField(default=django.utils.datetime_safe.date.today),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='01/26/2019', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='01/26/2018', max_length=32, verbose_name='Start Date'),
        ),
    ]
