from django.db import models


class ConsultationFormatsField(models.CharField):
    """
    Python side: a comma-separated string, e.g. 'video,audio,chat'.
    PostgreSQL side (db/schema.sql): consultation_format[], e.g. '{video,audio,chat}'.

    Without this, Django inserts the string 'video,audio,chat' into the enum-array column
    and PostgreSQL rejects it as a malformed array literal (breaking lawyer registration).
    """

    def db_type(self, connection):
        if connection.vendor == 'postgresql':
            return 'consultation_format[]'
        return super().db_type(connection)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared)
        if connection.vendor == 'postgresql' and isinstance(value, str):
            items = [v.strip() for v in value.strip('{}').split(',') if v.strip()]
            return '{' + ','.join(items) + '}'
        return value

    def from_db_value(self, value, expression, connection):
        if isinstance(value, (list, tuple)):
            return ','.join(value)
        if isinstance(value, str) and value.startswith('{'):
            return value.strip('{}')
        return value
