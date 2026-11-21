from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import lawyers.fields


class Migration(migrations.Migration):
    """
    State-only: db/schema.sql is the source of truth for the database. It names the foreign
    keys `verified_by` / `reviewed_by` and stores `formats` as consultation_format[].
    The models now match, so no SQL runs here (on a schema.sql database run
    `python manage.py migrate lawyers --fake` if 0001/0002 were never applied).
    """

    dependencies = [
        ('lawyers', '0002_alter_court_options_alter_practicearea_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='lawyerprofile',
                    name='formats',
                    field=lawyers.fields.ConsultationFormatsField(default='video,audio,chat', max_length=100),
                ),
                migrations.AlterField(
                    model_name='lawyerprofile',
                    name='verified_by',
                    field=models.ForeignKey(blank=True, db_column='verified_by', null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            related_name='verified_lawyers', to=settings.AUTH_USER_MODEL),
                ),
                migrations.AlterField(
                    model_name='lawyerverificationdocument',
                    name='reviewed_by',
                    field=models.ForeignKey(blank=True, db_column='reviewed_by', null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            related_name='reviewed_documents', to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
