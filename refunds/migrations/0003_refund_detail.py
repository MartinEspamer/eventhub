# Generated by Django 5.2 on 2025-04-30 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refunds', '0002_alter_refund_approval_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='detail',
            field=models.TextField(null=True),
        ),
    ]
