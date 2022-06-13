from django.urls import path
from boards import views

app_name = "boards"

urlpatterns = [
    # boards:
    path("", views.boards, name="boards"),
    path("create_board", views.create_board, name="create_board"),
    path("<uuid:board_uuid>", views.board, name="board"),
    # lists:
    path("<uuid:board_uuid>/create_list", views.create_list, name="create_list"),
    path(
        "<uuid:board_uuid>/<uuid:list_uuid>/delete_list",
        views.delete_list,
        name="delete_list",
    ),
    # tasks:
    path(
        "<uuid:board_uuid>/<uuid:list_uuid>/create_task",
        views.create_task,
        name="create_task",
    ),
    path(
        "<uuid:board_uuid>/<uuid:task_uuid>/edit_task",
        views.edit_task,
        name="edit_task",
    ),
    path(
        "<uuid:task_uuid>/task_modal",
        views.task_modal,
        name="task_modal",
    ),
    path("<uuid:board_uuid>/list_move", views.list_move, name="list_move"),
    path("<uuid:board_uuid>/task_move", views.task_move, name="task_move"),
]
