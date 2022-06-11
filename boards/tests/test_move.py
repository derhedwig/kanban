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
    driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()

    assert len(driver.find_elements(By.CLASS_NAME, "list")) == 4
    assert List.objects.count() == 4


def drag_and_drop(driver: WebDriver, source: WebElement, target: WebElement):
    driver.execute_script(
        """
        const source = arguments[0]
        const target = arguments[1]
        let dataTransfer = new DataTransfer
        source.dispatchEvent(new DragEvent('dragstart', {dataTransfer: dataTransfer}))
        target.dispatchEvent(new DragEvent('drop', {dataTransfer: dataTransfer}))
        target.dispatchEvent(new DragEvent('dragend', {dataTransfer: dataTransfer}))
    """,
        source,
        target,
    )


def test_move_list(live_server, driver: WebDriver, board: Board):
    driver.get(f"{live_server.url}{board.get_absolute_url()}")
    lists = List.objects.all()
    # assert lists[0].order < lists[1].order < lists[2].order
    time.sleep(2)

    list_els = driver.find_elements(By.CLASS_NAME, "list")
    source = list_els[2].find_element(By.CLASS_NAME, "list-handle")
    target = list_els[0]

    drag_and_drop(driver, source, target)

    # ActionChains(driver).click(source).pause(1).click_and_hold().pause(
    #     1
    # ).move_by_offset(-400, 0).release().perform()
    # ActionChains(driver).drag_and_drop_by_offset(source, -400, 0).perform()
    # ActionChains(driver).drag_and_drop(source, target).perform()

    # time.sleep(3)

    # assert lists[2].order < lists[1].order < lists[0].order


def test_test_move(driver: WebDriver):
    driver.get("http://the-internet.herokuapp.com/drag_and_drop")
    a = driver.find_element(By.ID, "column-a")
    b = driver.find_element(By.ID, "column-b")
    ActionChains(driver).drag_and_drop(a, b).perform()


def test_move_tasks_from_list_to_list(live_server, driver: WebDriver, board):
    task = Task.objects.create(label="Test Task", list=board.lists.first())
    driver.get(f"{live_server.url}{board.get_absolute_url()}")

    time.sleep(3)

    task_element = driver.find_element(By.CLASS_NAME, "task")
    list_elements = driver.find_elements(By.CSS_SELECTOR, ".list .sortable-tasks")

    action = ActionChains(driver)
    action.drag_and_drop(task_element, list_elements[1]).perform()

    # driver.get(f"{live_server.url}{board.get_absolute_url()}")

    task.refresh_from_db()
    assert task.list == board.lists.all()[1]
