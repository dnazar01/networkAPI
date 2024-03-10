import requests, re
from http import HTTPStatus
from additional_functions import create_user_payload

ENDPOINT = "http://127.0.0.1:5000"


def test_create_get_user():
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    payload = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert created_response.status_code == HTTPStatus.OK

    # проверяем что пользователь корректно создался
    assert created_response.json()["first_name"] == payload["first_name"]
    assert created_response.json()["last_name"] == payload["last_name"]
    assert created_response.json()["email"] == payload["email"]

    # проверяем что пользователя можно достать через /users/id
    user_id = created_response.json()["id"]
    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert get_response.json()["first_name"] == payload["first_name"]
    assert get_response.json()["last_name"] == payload["last_name"]
    assert get_response.json()["email"] == payload["email"]

    # удаляем и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.json()["first_name"] == payload["first_name"]
    assert delete_response.json()["last_name"] == payload["last_name"]
    assert delete_response.json()["status"] == "deleted"


def test_create_user_with_wrong_data():
    payload = create_user_payload()
    payload["email"] = "testtest"

    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert created_response.status_code == HTTPStatus.BAD_REQUEST


def test_create_users_leaderboard_list():
    n = 3
    test_users = []
    for _ in range(n):
        payload = create_user_payload()
        created_response = requests.post(f"{ENDPOINT}/users/create", json=payload)
        assert created_response.status_code == HTTPStatus.OK
        test_users.append(created_response.json()["id"])

    payload = {"type": "list", "sort": "asc"}
    get_response = requests.get(f"{ENDPOINT}/users/leaderboard", json=payload)
    leaderboard = get_response.json()["users"]
    assert isinstance(leaderboard, list)
    assert len(leaderboard) == n

    for user_id in test_users:
        delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
        assert delete_response.status_code == HTTPStatus.OK


def test_create_users_leaderboard_graph():
    # создаем запрос на граф
    payload = {"type": "graph"}
    created_response = requests.get(f"{ENDPOINT}/users/leaderboard", json=payload)
    assert created_response.status_code == HTTPStatus.OK

    # проверка того, соответствует ли строка ответа нашим ожиданиям
    pattern = r'<img\s+src="([^"]+)"'
    assert re.match(pattern, created_response.text)

    # не включаем '<img src=" и ">, проверка, что по такому адресу можно перейти и график появился
    path = created_response.text[10:-2]
    get_response = requests.get(f"{ENDPOINT}/{path}")
    assert get_response.status_code == HTTPStatus.OK
