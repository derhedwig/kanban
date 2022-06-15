from boards.models import Task, Board, List
import time

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains


def test_visit_board(live_server, driver: WebDriver, board: Board):
    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    assert board.name in driver.page_source
    assert board.lists.count() == 3


def test_create_task(live_server, driver: WebDriver, board: Board):
    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    driver.find_element(By.CLASS_NAME, "create-task-button").click()
    driver.switch_to.active_element.send_keys("Test Aufgabe")
    driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()

    assert len(driver.find_elements(By.CLASS_NAME, "task")) == 1
    assert Task.objects.count() == 1


def test_create_list(live_server, driver: WebDriver, board: Board):
    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    driver.find_element(By.CLASS_NAME, "create-list-button").click()
    driver.switch_to.active_element.send_keys("Test Liste")
    driver.find_element(By.CSS_SELECTOR, ".create-list-form [type='submit']").click()

    assert len(driver.find_elements(By.CLASS_NAME, "list")) == 4
    assert List.objects.count() == 4


def test_move_list(live_server, driver: WebDriver, board: Board):
    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    lists = List.objects.all()
    assert ["Todo", "Doing", "Done"] == [list.name for list in lists]

    list_els = driver.find_elements(By.CLASS_NAME, "list")
    source = list_els[2].find_element(By.CLASS_NAME, "list-handle h2")

    # drag and drop last list to first list
    ActionChains(driver).drag_and_drop_by_offset(source, -400, 0).perform()

    # re-get page
    driver.get(f"{live_server.url}{board.get_absolute_url()}")

    # check list order visually
    list_els = driver.find_elements(By.CLASS_NAME, "list h2 span:first-of-type")
    assert ["Done", "Todo", "Doing"] == [list.text for list in list_els]

    # check list order in db
    lists = List.objects.all()
    assert ["Done", "Todo", "Doing"] == [list.name for list in lists]


def test_move_tasks_from_list_to_list(live_server, driver: WebDriver, board):
    task = Task.objects.create(label="Test Task", list=board.lists.first())

    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    task_element = driver.find_element(By.CLASS_NAME, "task")
    list_elements = driver.find_elements(By.CSS_SELECTOR, ".list .sortable-tasks")

    # drag and drop to second list
    ActionChains(driver).drag_and_drop(task_element, list_elements[1]).perform()

    # re-get page
    driver.get(f"{live_server.url}{board.get_absolute_url()}")

    # Test Task is now visibly in the second list
    list_elements = driver.find_elements(By.CSS_SELECTOR, ".list .sortable-tasks")
    "Test Task" in list_elements[1].text

    # also in the db
    task.refresh_from_db()
    assert task.list.name == board.lists.all()[1].name


# TODO: reorder task in a list

# TODO: move task from list to list to a specific position
