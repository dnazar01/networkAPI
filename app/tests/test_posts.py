import requests
from http import HTTPStatus
from additional_functions import create_post_payload, create_user_payload

ENDPOINT = 'http://127.0.0.1:5000'


def test_create_get_post():
    payload = create_user_payload()
    created_response = requests.post(f"{ENDPOINT}/users/create", json=payload)
    assert created_response.status_code == HTTPStatus.OK

    user_id = created_response.json()['id']
    assert created_response.json()['first_name'] == payload['first_name']
    assert created_response.json()['last_name'] == payload['last_name']
    assert created_response.json()['email'] == payload['email']

    get_response = requests.get(f"{ENDPOINT}/users/{user_id}")
    assert get_response.json()['first_name'] == payload['first_name']
    assert get_response.json()['last_name'] == payload['last_name']
    assert get_response.json()['email'] == payload['email']

    payload = create_post_payload()
    payload['author_id'] = user_id
    created_response = requests.post(f"{ENDPOINT}/posts/create", json=payload)
    assert created_response.status_code == HTTPStatus.OK

    post_id = created_response.json()['id']
    get_response = requests.get(f"{ENDPOINT}/posts/{post_id}")
    assert get_response.json()['id'] == post_id
    assert get_response.json()['author_id'] == payload['author_id']
    assert get_response.json()['text'] == payload['text']
    assert isinstance(get_response.json()['reactions'], list)
