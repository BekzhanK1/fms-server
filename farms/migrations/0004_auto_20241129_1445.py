# Generated by Django 3.1.12 on 2024-11-29 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farms', '0003_farm_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='farm',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
