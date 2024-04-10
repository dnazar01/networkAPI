import requests, re
from http import HTTPStatus
from app.tests.utils import create_user_payload, to_specific_dict
from app.tests import ENDPOINT


def test_create_get_user(create_user_payload):
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    created_response = requests.post(
        f"{ENDPOINT}/users/create", json=create_user_payload
    )
    created_response_json = created_response.json()
    assert created_response.status_code == HTTPStatus.OK

    # проверяем что пользователь корректно создался
    assert (
        to_specific_dict(created_response_json, "first_name", "last_name", "email")
        == create_user_payload
    )

    # проверяем что пользователя можно достать через /users/id
    user_id = created_response.json()["id"]
    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert (
        to_specific_dict(get_response.json(), "first_name", "last_name", "email")
        == create_user_payload
    )

    # удаляем и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    delete_response_json = delete_response.json()
    assert to_specific_dict(
        delete_response_json, "first_name", "last_name"
    ) == to_specific_dict(create_user_payload, "first_name", "last_name")
    assert delete_response_json["status"] == "deleted"


def test_create_user_with_wrong_data(create_user_payload):
    create_user_payload["email"] = "testtest"

    created_response = requests.post(
        f"{ENDPOINT}/users/create", json=create_user_payload
    )
    assert created_response.status_code == HTTPStatus.BAD_REQUEST


def test_create_users_leaderboard_list(create_user_payload):
    n = 3
    test_users = []
    for _ in range(n):
        created_response = requests.post(
            f"{ENDPOINT}/users/create", json=create_user_payload
        )
        assert created_response.status_code == HTTPStatus.OK
        test_users.append(created_response.json()["id"])

    payload = {"type": "list", "sort": "asc"}
    get_response = requests.get(f"{ENDPOINT}/users/leaderboard", json=payload)
    leaderboard = get_response.json()["users"]
    assert isinstance(leaderboard, list) and len(leaderboard) == n

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
