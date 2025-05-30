# Generated by Django 5.2.1 on 2025-05-25 11:20

import community_app.storage
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_app', '0002_alter_community_cover_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitymessage',
            name='attachment',
            field=models.FileField(blank=True, null=True, storage=community_app.storage.CommunityAttachmentStorage(), upload_to='community_attachments/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'])]),
        ),
    ]
