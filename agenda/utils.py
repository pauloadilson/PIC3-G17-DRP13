import requests
from microsoft_authentication.auth_helper import get_token
from microsoft_authentication.graph_helper import graph_url


def criar_evento_no_microsoft_graph(evento):
    print('Entrando em criar evento')
    access_token = get_token(requests)
    url = f"{graph_url}/me/events"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    evento_data = {
        "subject": evento.titulo,
        "body": {
            "contentType": "HTML",
            "content": evento.descricao,
        },
        "start": {
            "dateTime": evento.data_inicio.isoformat(),
            "timeZone": "America/Sao_Paulo",
        },
        "end": {
            "dateTime": evento.data_fim.isoformat(),
            "timeZone": "America/Sao_Paulo",
        },
        "location": {
            "displayName": evento.local,
        },
    }

    response = requests.post(url, json=evento_data, headers=headers)

    if response.status_code == 201:
        return response.json()  # Evento criado com sucesso
    else:
        raise Exception(f"Erro ao criar evento: {response.content}")
