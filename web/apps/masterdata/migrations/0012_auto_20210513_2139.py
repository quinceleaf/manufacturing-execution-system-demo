# Generated by Django 3.2.1 on 2021-05-13 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0011_alter_billofmaterials_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalitem',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalmaterial',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalproduct',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='archive',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='historicalitem',
            name='unit_type',
            field=models.CharField(choices=[('WEIGHT', 'Weight'), ('VOLUME', 'Volume'), ('EACH', 'Each')], default='WEIGHT', max_length=32, verbose_name='Unit Type'),
        ),
        migrations.AlterField(
            model_name='historicalmaterial',
            name='unit_type',
            field=models.CharField(choices=[('WEIGHT', 'Weight'), ('VOLUME', 'Volume'), ('EACH', 'Each')], default='WEIGHT', max_length=32, verbose_name='Unit Type'),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='unit_type',
            field=models.CharField(choices=[('WEIGHT', 'Weight'), ('VOLUME', 'Volume'), ('EACH', 'Each')], default='WEIGHT', max_length=32, verbose_name='Unit Type'),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit_type',
            field=models.CharField(choices=[('WEIGHT', 'Weight'), ('VOLUME', 'Volume'), ('EACH', 'Each')], default='WEIGHT', max_length=32, verbose_name='Unit Type'),
        ),
    ]