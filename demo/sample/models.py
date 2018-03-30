from django.db import models


class DemoModel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    document = models.FileField()


class DemoChildModel(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(DemoModel, related_name="children")
