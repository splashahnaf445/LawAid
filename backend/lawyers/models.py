"""Reference tables needed by lawyer registration. Lawyer search/availability come in later tickets."""
from django.db import models


class Court(models.Model):
    name = models.TextField(unique=True)
    court_type = models.TextField()
    district = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "courts"
        managed = False
        ordering = ["name"]

    def __str__(self):
        return self.name


class PracticeArea(models.Model):
    slug = models.TextField(unique=True)
    name_en = models.TextField()
    name_bn = models.TextField()

    class Meta:
        db_table = "practice_areas"
        managed = False
        ordering = ["id"]

    def __str__(self):
        return self.name_en
