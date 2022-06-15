import uuid

from django.db import models
from django.urls import reverse


class Board(models.Model):
    name = models.CharField("Name", max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_absolute_url(self):
        return reverse("boards:board", kwargs={"board_uuid": self.uuid})

    def create_default_lists(self):
        for name in ["Todo", "Doing", "Done"]:
            List.objects.create(name=name, board=self)

    def __str__(self) -> str:
        return self.name


class List(models.Model):
    name = models.CharField("Name", max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="lists")
    order = models.SmallIntegerField(default=1000, db_index=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.order})"

    class Meta:
        ordering = ["order"]


class Task(models.Model):
    label = models.TextField("Beschriftung")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="tasks")
    order = models.SmallIntegerField(default=1000, db_index=True)
    description = models.TextField("Beschreibung", blank=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        ordering = ["order"]
