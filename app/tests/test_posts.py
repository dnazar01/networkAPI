import requests
from http import HTTPStatus
from app.tests.utils import to_specific_dict, create_reaction_payload, create_user_payload, create_post_payload
from app.tests import ENDPOINT


def test_create_get_post(create_user_payload, create_post_payload):
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    created_response = requests.post(f"{ENDPOINT}/users/create", json=create_user_payload)
    assert created_response.status_code == HTTPStatus.OK

    # получили id
    user_id = created_response.json()["id"]

    # кинули запрос на создание поста
    create_post_payload["author_id"] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=create_post_payload)
    assert created_response.status_code == HTTPStatus.OK

    # проверили что он корректно создался и вернул правильные значения
    assert to_specific_dict(created_response.json(), "author_id", "text") == create_post_payload

    # проверили что можем к нему обратиться по id
    post_id = created_response.json()["id"]
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    get_response_json = get_response.json()  # сделали одно обращение вместо 3

    assert to_specific_dict(get_response_json, "author_id", "text") == create_post_payload
    assert get_response_json["id"] == post_id and isinstance(get_response_json["reactions"], list)

    # удаляем пользователя
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.status_code == HTTPStatus.OK

    # удаляем пост и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    delete_response_json = delete_response.json()

    assert to_specific_dict(delete_response_json, "author_id", "text") == create_post_payload
    assert delete_response_json["id"] == post_id and delete_response_json["status"] == "deleted" and isinstance(
        delete_response_json["reactions"], list)


def test_create_post_with_wrong_data(create_post_payload):
    # неправильный id у автора
    create_post_payload["author_id"] = 10 ** 9
    create_response = requests.post(f"{ENDPOINT}/posts/create", json=create_post_payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST


def test_posting_reaction(create_user_payload,create_post_payload, create_reaction_payload):
    # создать первого пользователя
    created_response = requests.post(f"{ENDPOINT}/users/create", json=create_user_payload)
    assert created_response.status_code == HTTPStatus.OK

    user_id_1 = created_response.json()["id"]

    # создать второго пользователя
    created_response = requests.post(f"{ENDPOINT}/users/create", json=create_user_payload)
    assert created_response.status_code == HTTPStatus.OK

    user_id_2 = created_response.json()[
        "id"]  # нет смысла выделять отдельный массив created_response_json так как каждый раз мы обращаемся к новому created_response

    # создать пост для первого пользователя
    create_post_payload["author_id"] = user_id_1
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=create_post_payload)
    assert created_response.status_code == HTTPStatus.OK

    post_id = created_response.json()["id"]

    # запостили реакцию и проверили что первому начислился балл
    create_reaction_payload["user_id"] = user_id_2
    created_request = requests.post(
        f"{ENDPOINT}/posts/{post_id}/reaction", json=create_reaction_payload
    )
    assert created_request.status_code == HTTPStatus.OK

    # проверка начисления балла пользователю
    get_response = requests.get(f"{ENDPOINT}/users/{user_id_1}")
    assert get_response.json()["total_reactions"] == 1

    # проверка, что у самого поста теперь появилась реакция
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()["reactions"] == ["boom"]  # то же новый запрос, нельзя соптимизировать

    # удаляем пользователей
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_1}")
    assert delete_response.status_code == HTTPStatus.OK

    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_2}")
    assert delete_response.status_code == HTTPStatus.OK

    # удаляем пост
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.status_code == HTTPStatus.OK


def test_all_posts(create_user_payload, create_post_payload, create_reaction_payload):
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    created_response = requests.post(f"{ENDPOINT}/users/create", json=create_user_payload)
    assert created_response.status_code == HTTPStatus.OK

    user_id = created_response.json()["id"]
    all_posts_id = []  # храним все айди созданных постов
    for _ in range(3):
        create_post_payload["author_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/create", json=create_post_payload
        )
        assert created_response.status_code == HTTPStatus.OK
        all_posts_id.append(
            created_response.json()["id"])  # каждый раз новый запрос, нет смысла его запоминать в массив

    # запускаем везде нужное количество реакций
    n = 5

    # на первый пост n реакции
    post_id = all_posts_id[0]
    for _ in range(n):
        create_reaction_payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=create_reaction_payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # на второй пост n-2 реакция
    post_id = all_posts_id[1]
    for _ in range(n - 2):
        create_reaction_payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=create_reaction_payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # на третий пост n+1 реакции
    post_id = all_posts_id[2]
    for _ in range(n + 1):
        create_reaction_payload["user_id"] = user_id
        created_response = requests.post(
            f"{ENDPOINT}/posts/{post_id}/reaction", json=create_reaction_payload
        )
        assert created_response.status_code == HTTPStatus.OK

    # ожидаемый массив после сортировки это [n,n-2,n+1] -> [n-2, n, n+1]
    # cравниваем ожидания с реальностью, сортировка по возрастанию
    payload = {"sort": "desc"}
    created_response = requests.get(f"{ENDPOINT}/users/{user_id}/posts", json=payload)
    created_response_json = created_response.json()
    assert created_response.status_code == HTTPStatus.OK
    assert isinstance(created_response_json["posts"], list)

    result_of_sort = [
        len(post["reactions"]) for post in created_response_json["posts"]
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
