import requests
from http import HTTPStatus
from additional_functions import create_post_payload, create_user_payload, create_reaction_payload

ENDPOINT = 'http://127.0.0.1:5000'


def test_create_get_post():
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    # проверяем что пользователь корректно создался
    assert created_response.json()['first_name'] == payload_for_user['first_name']
    assert created_response.json()['last_name'] == payload_for_user['last_name']
    assert created_response.json()['email'] == payload_for_user['email']

    # проверяем что пользователя можно достать через /users/id
    user_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert get_response.json()['first_name'] == payload_for_user['first_name']
    assert get_response.json()['last_name'] == payload_for_user['last_name']
    assert get_response.json()['email'] == payload_for_user['email']

    # кинули запрос на создание поста
    payload_for_post = create_post_payload()
    payload_for_post['author_id'] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    # проверили что он корректно создался и вернул правильные значения
    assert created_response.json()['author_id'] == payload_for_post['author_id']
    assert created_response.json()['text'] == payload_for_post['text']

    # проверили что можем к нему обратиться по id
    post_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()['id'] == post_id
    assert get_response.json()['author_id'] == payload_for_post['author_id']
    assert get_response.json()['text'] == payload_for_post['text']
    assert isinstance(get_response.json()['reactions'], list)

    # удаляем пользователя и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.json()['first_name'] == payload_for_user['first_name']
    assert delete_response.json()['last_name'] == payload_for_user['last_name']
    assert delete_response.json()['status'] == 'deleted'

    # удаляем пост и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.json()['id'] == post_id
    assert delete_response.json()['author_id'] == payload_for_post['author_id']
    assert delete_response.json()['text'] == payload_for_post['text']
    assert isinstance(delete_response.json()['reactions'], list)
    assert delete_response.json()['status'] == 'deleted'


def test_create_post_with_wrong_data():
    # неправильный id у автора
    payload = create_post_payload()
    payload["author_id"] = 10 ** 9
    create_response = requests.post(f"{ENDPOINT}/posts/create", json=payload)
    assert create_response.status_code == HTTPStatus.BAD_REQUEST


def test_posting_reaction():
    # создать первого пользователя
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    assert created_response.json()['first_name'] == payload_for_user['first_name']
    assert created_response.json()['last_name'] == payload_for_user['last_name']
    assert created_response.json()['email'] == payload_for_user['email']

    user_id_1 = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/users/{user_id_1}")
    assert get_response.json()['first_name'] == payload_for_user['first_name']
    assert get_response.json()['last_name'] == payload_for_user['last_name']
    assert get_response.json()['email'] == payload_for_user['email']

    # создать второго пользователя
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    assert created_response.json()['first_name'] == payload_for_user['first_name']
    assert created_response.json()['last_name'] == payload_for_user['last_name']
    assert created_response.json()['email'] == payload_for_user['email']

    user_id_2 = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/users/{user_id_2}")
    assert get_response.json()['first_name'] == payload_for_user['first_name']
    assert get_response.json()['last_name'] == payload_for_user['last_name']
    assert get_response.json()['email'] == payload_for_user['email']

    # создать пост для первого пользователя
    payload_for_post = create_post_payload()
    payload_for_post['author_id'] = user_id_1
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    assert created_response.json()['author_id'] == payload_for_post['author_id']
    assert created_response.json()['text'] == payload_for_post['text']

    post_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()['id'] == post_id
    assert get_response.json()['author_id'] == payload_for_post['author_id']
    assert get_response.json()['text'] == payload_for_post['text']
    assert isinstance(get_response.json()['reactions'], list)

    # запостили реакцию и проверили что первому начислился балл
    payload = create_reaction_payload()
    payload['user_id'] = user_id_2
    created_request = requests.post(f"{ENDPOINT}/posts/{post_id}/reaction", json=payload)
    assert created_request.status_code == HTTPStatus.OK
    # проверка начисления балла пользователю
    get_response = requests.get(f"{ENDPOINT}/users/{user_id_1}")
    assert get_response.json()["total_reactions"] == 1
    # проверка, что у самого поста теперь появилась реакция
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()["reactions"] == ["boom"]

    # удаляем пользователей
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_1}")
    assert delete_response.json()['first_name'] == payload_for_user['first_name']
    assert delete_response.json()['last_name'] == payload_for_user['last_name']
    assert delete_response.json()['status'] == 'deleted'

    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id_2}")
    assert delete_response.json()['first_name'] == payload_for_user['first_name']
    assert delete_response.json()['last_name'] == payload_for_user['last_name']
    assert delete_response.json()['status'] == 'deleted'

    # удаляем пост и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.json()['id'] == post_id
    assert delete_response.json()['author_id'] == payload_for_post['author_id']
    assert delete_response.json()['text'] == payload_for_post['text']
    assert isinstance(delete_response.json()['reactions'], list)
    assert delete_response.json()['status'] == 'deleted'


def test_all_posts():
    # прокинули запрос на создание пользователя, проверили что это можно сделать и создали
    payload_for_user = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload_for_user)
    assert created_response.status_code == HTTPStatus.OK

    # проверяем что пользователь корректно создался
    assert created_response.json()['first_name'] == payload_for_user['first_name']
    assert created_response.json()['last_name'] == payload_for_user['last_name']
    assert created_response.json()['email'] == payload_for_user['email']

    # проверяем что пользователя можно достать через /users/id
    user_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert get_response.json()['first_name'] == payload_for_user['first_name']
    assert get_response.json()['last_name'] == payload_for_user['last_name']
    assert get_response.json()['email'] == payload_for_user['email']

    # кинули запрос на создание поста 1
    payload_for_post = create_post_payload()
    payload_for_post['author_id'] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    # проверили что он корректно создался и вернул правильные значения
    assert created_response.json()['author_id'] == payload_for_post['author_id']
    assert created_response.json()['text'] == payload_for_post['text']

    # проверили что можем к нему обратиться по id
    post_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()['id'] == post_id
    assert get_response.json()['author_id'] == payload_for_post['author_id']
    assert get_response.json()['text'] == payload_for_post['text']
    assert isinstance(get_response.json()['reactions'], list)

    # кинули запрос на создание поста 2
    payload_for_post = create_post_payload()
    payload_for_post['author_id'] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload_for_post)
    assert created_response.status_code == HTTPStatus.OK

    # проверили что он корректно создался и вернул правильные значения
    assert created_response.json()['author_id'] == payload_for_post['author_id']
    assert created_response.json()['text'] == payload_for_post['text']

    # проверили что можем к нему обратиться по id
    post_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()['id'] == post_id
    assert get_response.json()['author_id'] == payload_for_post['author_id']
    assert get_response.json()['text'] == payload_for_post['text']
    assert isinstance(get_response.json()['reactions'], list)



    # удаляем пользователя и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/users/{user_id}")
    assert delete_response.json()['first_name'] == payload_for_user['first_name']
    assert delete_response.json()['last_name'] == payload_for_user['last_name']
    assert delete_response.json()['status'] == 'deleted'

    # удаляем пост и поверяем что нам вернулась нужная информация
    delete_response = requests.delete(f"{ENDPOINT}/posts/{post_id}")
    assert delete_response.json()['id'] == post_id
    assert delete_response.json()['author_id'] == payload_for_post['author_id']
    assert delete_response.json()['text'] == payload_for_post['text']
    assert isinstance(delete_response.json()['reactions'], list)
    assert delete_response.json()['status'] == 'deleted'




