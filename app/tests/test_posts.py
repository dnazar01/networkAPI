import requests
from http import HTTPStatus
from app.tests.utils import (
    create_post_payload,
    create_user_payload,
    create_reaction_payload,
)
from app.tests import ENDPOINT

def test_create_get_post():
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    # получили id
    user_id = created_response.json()["id"]

    # кинули запрос на создание поста
    payload_for_post = create_post_payload()
    payload_for_post["author_id"] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    # проверили что он корректно создался и вернул правильные значения
    assert created_response.json()["author_id"] == payload_for_post["author_id"]
    assert created_response.json()["text"] == payload_for_post["text"]

    # проверили что можем к нему обратиться по id
    post_id = created_response.json()["id"]
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()["id"] == post_id
    assert get_response.json()["author_id"] == payload_for_post["author_id"]
    assert get_response.json()["text"] == payload_for_post["text"]
    assert isinstance(get_response.json()["reactions"], list)

    # удаляем пользователя
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.status_code == HTTPStatus.OK

    # удаляем пост и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.json()["id"] == post_id
    assert delete_response.json()["author_id"] == payload_for_post["author_id"]
    assert delete_response.json()["text"] == payload_for_post["text"]
    assert isinstance(delete_response.json()["reactions"], list)
    assert delete_response.json()["status"] == "deleted"


def test_create_post_with_wrong_data():
    # неправильный id у автора
    payload = create_post_payload()
    payload["author_id"] = 10**9
    create_response = requests.post(f"{ENDPOINT}/posts/create", json=payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST


def test_posting_reaction():
    # создать первого пользователя
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    user_id_1 = created_response.json()["id"]

    # создать второго пользователя
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    user_id_2 = created_response.json()["id"]

    # создать пост для первого пользователя
    payload_for_post = create_post_payload()
    payload_for_post["author_id"] = user_id_1
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    post_id = created_response.json()["id"]

    # запостили реакцию и проверили что первому начислился балл
    payload = create_reaction_payload()
    payload["user_id"] = user_id_2
    created_request = requests.post(
        f"{ENDPOINT}/posts/{post_id}/reaction", json=payload
    )
    assert created_request.status_code == HTTPStatus.OK

    # проверка начисления балла пользователю
    get_response = requests.get(f"{ENDPOINT}/users/{user_id_1}")
    assert get_response.json()["total_reactions"] == 1

    # проверка, что у самого поста теперь появилась реакция
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()["reactions"] == ["boom"]

    # удаляем пользователей
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_1}")
    assert delete_response.status_code == HTTPStatus.OK

    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_2}")
    assert delete_response.status_code == HTTPStatus.OK

    # удаляем пост
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.status_code == HTTPStatus.OK


def test_all_posts():
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    user_id = created_response.json()["id"]
    all_posts_id = []  # храним все айди созданных постов
    for _ in range(3):
        payload_for_post = create_post_payload()
        payload_for_post["author_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/create", json=payload_for_post
        )
        assert created_response.status_code == HTTPStatus.OK
        all_posts_id.append(created_response.json()["id"])

    # запускаем везде нужное количество реакций
    n = 5

    # на первый пост n реакции
    post_id = all_posts_id[0]
    for _ in range(n):
        payload = create_reaction_payload()
        payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # на второй пост n-2 реакция
    post_id = all_posts_id[1]
    for _ in range(n - 2):
        payload = create_reaction_payload()
        payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # на третий пост n+1 реакции
    post_id = all_posts_id[2]
    for _ in range(n + 1):
        payload = create_reaction_payload()
        payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # ожидаемый массив после сортировки это [n,n-2,n+1] -> [n-2, n, n+1]
    # cравниваем ожидания с реальностью, сортировка по возрастанию
    payload = {"sort": "desc"}
    created_response = requests.get(f"{ENDPOINT}/users/{user_id}/posts", json=payload)
    assert created_response.status_code == HTTPStatus.OK
    assert isinstance(created_response.json()["posts"], list)

    result_of_sort = [
        len(post["reactions"]) for post in created_response.json()["posts"]
    ]

    # сразу проверяем по нужному количеству реакций
    expected = [n - 2, n, n + 1]
    assert result_of_sort == (expected if payload["sort"] == "asc" else expected[::-1])

    # удалили все посты
    for post_id in all_posts_id:
        delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
        assert delete_response.status_code == HTTPStatus.OK

    # удалили пользователя
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.status_code == HTTPStatus.OK
