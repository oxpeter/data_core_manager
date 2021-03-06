# Generated by Django 2.0 on 2018-03-06 03:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dc_management', '0042_auto_20180302_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dcuagenerator',
            name='enddate',
            field=models.CharField(default='03/05/2019', max_length=32, verbose_name='End Date'),
        ),
        migrations.AlterField(
            model_name='dcuagenerator',
            name='startdate',
            field=models.CharField(default='03/05/2018', max_length=32, verbose_name='Start Date'),
        ),
        migrations.AlterField(
            model_name='migrationlog',
            name='access_date',
            field=models.DateField(blank=True, null=True, verbose_name='access confirmation date'),
        ),
        migrations.AlterField(
            model_name='migrationlog',
            name='data_date',
            field=models.DateField(blank=True, null=True, verbose_name='data integrity confirmation date'),
        ),
        migrations.AlterField(
            model_name='migrationlog',
            name='envt_date',
            field=models.DateField(blank=True, null=True, verbose_name='environment confirmation date'),
        ),
        migrations.AlterField(
            model_name='migrationlog',
            name='node_origin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='migration_origin', to='dc_management.Server'),
        ),
    ]
