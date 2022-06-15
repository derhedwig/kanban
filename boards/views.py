import uuid
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django import forms
from django.db.models import Case, When, F
from django.db import models
from django.views.decorators.http import require_POST

from boards.models import Board, List, Task


def boards(request):
    boards = Board.objects.all()
    return render(request, "boards/boards.html", {"boards": boards})


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["name"]


def create_board(request):
    form = BoardForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        board = form.save()
        board.create_default_lists()
        return HttpResponse(
            status=204, headers={"HX-Redirect": board.get_absolute_url()}
        )

    return render(request, "boards/board_form.html", {"form": form})


def board(request, board_uuid, partial=False):
    board = get_object_or_404(
        Board.objects.all().prefetch_related("lists__tasks"), uuid=board_uuid
    )
    template = "boards/_board.html" if partial else "boards/board.html"
    response = render(request, template, {"board": board})
    response["HX-Retarget"] = "#board"
    return response


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name"]


def create_list(request, board_uuid):
    board_ = get_object_or_404(Board, uuid=board_uuid)
    form = ListForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.board = board_
        form.save()
        return board(request, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"form": form})


def delete_list(request, board_uuid, list_uuid):
    list = get_object_or_404(List, uuid=list_uuid)

    if request.method == "POST":
        list.delete()

    return board(request, board_uuid, partial=True)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["label", "description"]


def create_task(request, board_uuid, list_uuid):
    list = get_object_or_404(List, uuid=list_uuid)
    form = TaskForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.list = list
        task = form.save()
        return board(request, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"form": form})


def edit_task(request, board_uuid, task_uuid):
    task = get_object_or_404(Task, uuid=task_uuid)
    form = TaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = form.save()
        return board(request, board_uuid, partial=True)

    return render(request, "boards/board_form.html", {"form": form})


class TypedMultipleField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, coerce, **kwargs):
        super().__init__(*args, **kwargs)
        self.coerce = self.coerce

    def valid_value(self, value):
        # all choices are okay
        return True


class ListMoveForm(forms.Form):
    list_uuids = TypedMultipleField(coerce=uuid.UUID)


def preserve_order(uuids):
    return Case(
        *[When(uuid=uuid, then=o) for o, uuid in enumerate(uuids)],
        default=F("order"),
        output_field=models.IntegerField()
    )


@require_POST
def list_move(request, board_uuid):
    form = ListMoveForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(str(form.errors))

    list_uuids = form.cleaned_data["list_uuids"]
    List.objects.filter(uuid__in=list_uuids).update(order=preserve_order(list_uuids))
    return board(request, board_uuid, partial=True)


class TaskMoveForm(forms.Form):
    item = forms.UUIDField()
    from_list = forms.UUIDField()
    to_list = forms.UUIDField()
    task_uuids = TypedMultipleField(coerce=uuid.UUID)


@require_POST
def task_move(request, board_uuid):
    form = TaskMoveForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(str(form.errors))

    from_list = form.cleaned_data["from_list"]
    to_list = form.cleaned_data["to_list"]
    task_uuids = form.cleaned_data["task_uuids"]
    item_uuid = form.cleaned_data["item"]

    if to_list == from_list:
        Task.objects.filter(uuid__in=task_uuids).update(
            order=preserve_order(task_uuids)
        )
    else:
        Task.objects.filter(uuid__in=task_uuids).update(
            order=preserve_order(task_uuids),
            list_id=List.objects.filter(uuid=to_list).order_by().values("id"),
        )

    return board(request, board_uuid, partial=True)


def task_modal(request, task_uuid):
    task = get_object_or_404(Task.objects.select_related("list"), uuid=task_uuid)
    form = TaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = form.save()
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})

    return render(request, "boards/task_modal.html", {"task": task, "form": form})
