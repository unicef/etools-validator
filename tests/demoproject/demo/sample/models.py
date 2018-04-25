from django.db import models
from django_fsm import FSMField, transition

from etools_validator.exceptions import TransitionError


class DemoModel(models.Model):
    STATUS_NEW = "new"
    STATUS_PENDING = "pending"
    STATUS_END = "end"
    STATUS_CHOICES = ((STATUS_NEW, "New"),
                      (STATUS_PENDING, "Pending"),
                      (STATUS_END, "End"),
                      )

    AUTO_TRANSITIONS = {STATUS_NEW: [STATUS_PENDING, STATUS_END],
                        STATUS_PENDING: [STATUS_END]
                        }

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    document = models.FileField(null=True, blank=True)
    status = FSMField(default=STATUS_NEW, choices=STATUS_CHOICES)

    def permission_structure(self):
        return None

    def can_complete(self):
        if not self.document:
            raise TransitionError(["Document is required"])
        return True

    def can_pend(self):
        return True

    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_PENDING, STATUS_END],
        target=[STATUS_END],
        conditions=[can_complete]
    )
    def complete(self):
        self.status = self.STATUS_END
        self.save()

    @transition(
        field=status,
        source=[STATUS_NEW, STATUS_PENDING],
        target=[STATUS_PENDING],
        conditions=[can_pend],
        permission="sample.can_change_to_pending"
    )
    def pend(self):
        self.status = self.STATUS_PENDING
        self.save()


class DemoModelNoAuto(DemoModel):
    AUTO_TRANSITIONS = {}


class DemoChildModel(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(DemoModel, on_delete=models.CASCADE, related_name="children")
