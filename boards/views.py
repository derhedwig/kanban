from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django import forms
from django.db import transaction
from django.db.models import Case, When

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


def preserve_order(uuids):
    return Case(*[When(uuid=uuid, then=o) for o, uuid in enumerate(uuids)])


def move(request, board_uuid):
    # <QueryDict: {'lists': ['3', '4', '5'], '5': ['3'], '4': ['1', '2']>
    from django.db import connection

    connection.queries.clear()

    with transaction.atomic():
        list_uuids = request.POST.getlist("lists")
        lists = List.objects.filter(uuid__in=list_uuids).order_by(
            preserve_order(list_uuids)
        )
        for list_order, list in enumerate(lists):
            list.order = list_order
            list.save()

            task_uuids = request.POST.getlist(str(list.uuid))
            tasks = Task.objects.filter(uuid__in=task_uuids).order_by(
                preserve_order(task_uuids)
            )
            for task_order, task in enumerate(tasks):
                task.order = task_order
                task.list = list
            Task.objects.bulk_update(tasks, ["order", "list_id"])

    print(len(connection.queries))
    for query in connection.queries:
        print(query)

    return board(request, board_uuid, partial=True)


def task_modal(request, task_uuid):
    task = get_object_or_404(Task, uuid=task_uuid)
    form = TaskForm(request.POST or None, instance=task)

    if request.method == "POST" and form.is_valid():
        task = form.save()
        return HttpResponse(status=204, headers={"HX-Refresh": "true"})

    return render(request, "boards/task_modal.html", {"task": task, "form": form})
