from django.db import models


class DemoModel(models.Model):
    STATUS_NEW = "new"
    STATUS_PENDING = "pending"
    STATUS_END = "end"
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_PENDING, "Pending"),
        (STATUS_END, "End"),
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    document = models.FileField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def permission_structure(self):
        return None


class DemoChildModel(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(DemoModel, related_name="children")
