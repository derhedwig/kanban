import pytest

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from boards.models import Board


@pytest.fixture(scope="session")
def driver():
    options = Options()
    # options.headless = True
    driver_ = webdriver.Firefox(options=options)
    yield driver_
    # driver_.quit()


# @pytest.fixture()
# def adriver(driver, client, live_server, user, settings) -> webdriver.Firefox:
#     """Return a browser instance with logged-in user session."""
#     settings.SITE_URL = live_server.url
#     client.login(username=user.username, password="secret")
#     cookie = client.cookies["sessionid"]
#     driver.get(live_server.url)
#     driver.add_cookie(
#         {"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"}
#     )
#     driver.refresh()
#     return driver


# @pytest.fixture
# def user(org) -> User:
#     user = User.objects.create_user(
#         first_name="Test",
#         last_name="User",
#         username="testuser",
#         email="test@example.com",
#         password="secret",
#     )
#     org.members.add(user)
#     return user


@pytest.fixture
def board():
    board = Board.objects.create(name="Test Board")
    board.create_default_lists()
    board.refresh_from_db()
    return board
