import requests
from microsoft_authentication.auth_helper import get_token

graph_url = 'https://graph.microsoft.com/v1.0'


def get_user(token):
    # Send GET to /me
    user = requests.get(
        f'{graph_url}/me',
        headers={'Authorization': f"Bearer {token}"},
        params={
            '$select': 'displayName,mail,mailboxSettings,userPrincipalName'})
    return user.json()


def get_calendar_events(token):
    # Send GET to /me/events
    events = requests.get(
        f'{graph_url}/me/events',
        headers={'Authorization': f"Bearer {token}"},
        params={'$select': 'subject,start,end, loccation'})
    return events.json()


def criar_evento_no_microsoft_graph(request, evento):
    print('Entrando em criar evento')
    access_token = get_token(request)
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
