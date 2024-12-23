# Generated by Django 4.2.7 on 2024-12-22 22:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'API Key',
                'verbose_name_plural': 'API Keys',
            },
        ),
        migrations.CreateModel(
            name='APIRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('status_code', models.IntegerField()),
                ('response_time', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.CharField(max_length=255)),
                ('api_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='api.apikey')),
            ],
            options={
                'verbose_name': 'API Request',
                'verbose_name_plural': 'API Requests',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='APIRateLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requests_per_minute', models.PositiveIntegerField(default=60)),
                ('requests_per_hour', models.PositiveIntegerField(default=1000)),
                ('requests_per_day', models.PositiveIntegerField(default=10000)),
                ('api_key', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rate_limit', to='api.apikey')),
            ],
            options={
                'verbose_name': 'API Rate Limit',
                'verbose_name_plural': 'API Rate Limits',
            },
        ),
    ]
