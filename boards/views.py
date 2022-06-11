from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django import forms
from django.db import transaction

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
    return render(request, template, {"board": board})


class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ["name"]


def create_list(request, board_uuid):
    board_ = get_object_or_404(Board, uuid=board_uuid)
    form = ListForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.instance.board = board_
        list = form.save()
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
        widgets = {"label": forms.TextInput}


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


def move(request, board_uuid):
    # <QueryDict: {'lists': ['3', '4', '5'], '5': ['3'], '4': ['1', '2']>
    from django.db import connection

    list_uuids = request.POST.getlist("lists")
    with transaction.atomic():
        list_order = 1
        for list_uuid in list_uuids:
            list = List.objects.get(uuid=list_uuid)
            list.order = list_order
            list.save()
            list_order += 1

            task_order = 1
            task_uuids = request.POST.getlist(list_uuid)
            for task_uuid in task_uuids:
                Task.objects.filter(uuid=task_uuid).update(order=task_order, list=list)
                task_order += 1

    print(len(connection.queries))
    print(connection.queries)

    return board(request, board_uuid, partial=True)


def task_modal(request, task_uuid):
    task = get_object_or_404(Task, uuid=task_uuid)
    form = TaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = form.save()
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})

    return render(request, "boards/task_modal.html", {"task": task, "form": form})
