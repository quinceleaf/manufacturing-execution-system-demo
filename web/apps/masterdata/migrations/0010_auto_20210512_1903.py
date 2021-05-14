# Generated by Django 3.2.1 on 2021-05-12 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masterdata', '0009_auto_20210512_0034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billofmaterials',
            name='product',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bills_of_materials', to='masterdata.product'),
        ),
        migrations.AlterField(
            model_name='historicalitem',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Products are available for sale once Approved and if set as Available', verbose_name='Available to Sales'),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_alcohol',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain alcohol?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_crustacea',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_dairy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain dairy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_egg',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain egg?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_fish',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain fish?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_gelatin',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain gelatin?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_honey',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain honey?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_meat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain meat/meat products?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_peanut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain peanuts?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_sesame',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain sesame?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_soy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain soy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_treenut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain treenuts (not peanuts)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalitemcharacteristics',
            name='contains_wheat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain wheat?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterial',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Products are available for sale once Approved and if set as Available', verbose_name='Available to Sales'),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_alcohol',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain alcohol?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_crustacea',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_dairy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain dairy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_egg',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain egg?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_fish',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain fish?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_gelatin',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain gelatin?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_honey',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain honey?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_meat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain meat/meat products?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_peanut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain peanuts?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_sesame',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain sesame?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_soy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain soy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_treenut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain treenuts (not peanuts)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalmaterialcharacteristics',
            name='contains_wheat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain wheat?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproduct',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Products are available for sale once Approved and if set as Available', verbose_name='Available to Sales'),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_alcohol',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain alcohol?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_crustacea',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_dairy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain dairy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_egg',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain egg?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_fish',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain fish?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_gelatin',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain gelatin?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_honey',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain honey?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_meat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain meat/meat products?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_peanut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain peanuts?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_sesame',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain sesame?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_soy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain soy?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_treenut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain treenuts (not peanuts)?', null=True),
        ),
        migrations.AlterField(
            model_name='historicalproductcharacteristics',
            name='contains_wheat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain wheat?', null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='is_available',
            field=models.BooleanField(default=True, help_text='Products are available for sale once Approved and if set as Available', verbose_name='Available to Sales'),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_alcohol',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain alcohol?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_crustacea',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain crustacean shellfish (crab, lobster or shrimp)?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_dairy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain dairy?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_egg',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain egg?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_fish',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain fish?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_gelatin',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain gelatin?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_honey',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain honey?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_meat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain meat/meat products?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_peanut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain peanuts?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_sesame',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain sesame?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_soy',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain soy?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_treenut',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain treenuts (not peanuts)?', null=True),
        ),
        migrations.AlterField(
            model_name='itemcharacteristics',
            name='contains_wheat',
            field=models.BooleanField(blank=True, default=None, help_text='Does this material or product contain wheat?', null=True),
        ),
    ]