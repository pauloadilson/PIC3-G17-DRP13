import msal
from django.conf import settings as django_settings


def load_cache(request):
    # Check for a token cache in the session
    cache = msal.SerializableTokenCache()
    if request.session.get('token_cache'):
        cache.deserialize(request.session['token_cache'])
    return cache


def save_cache(request, cache):
    # If cache has changed, persist back to session
    if cache.has_state_changed:
        request.session['token_cache'] = cache.serialize()


def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        django_settings.MICROSOFT_AUTH_CLIENT_ID,
        authority=django_settings.MICROSOFT_AUTH_TENANT_ID,
        client_credential=django_settings.MICROSOFT_AUTH_CLIENT_SECRET,
        token_cache=cache)
    return auth_app


def get_sign_in_flow():
    # Method to generate a sign-in flow
    auth_app = get_msal_app()
    return auth_app.initiate_auth_code_flow(
        django_settings.MICROSOFT_AUTH_SCOPES,
        redirect_uri=django_settings.MICROSOFT_AUTH_REDIRECT_URI)


def get_token_from_code(request):
    # Method to exchange auth code for access token
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    # Get the flow saved in session
    flow = request.session.pop('auth_flow', {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)
    return result


def store_user(request, user):
    try:
        request.session['user'] = {
            'is_authenticated': True,
            'name': user['displayName'],
            'email': user['mail'] if (user['mail'] is not None) else user['userPrincipalName'],
            'timeZone': user['mailboxSettings']['timeZone'] if (user['mailboxSettings']['timeZone'] is not None) else 'UTC'
        }
    except Exception as e:
        print(e)


def get_token(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(
            django_settings.MICROSOFT_AUTH_SCOPES,
            account=accounts[0])
        save_cache(request, cache)

        return result['access_token']


def remove_user_and_token(request):
    if 'token_cache' in request.session:
        del request.session['token_cache']

    if 'user' in request.session:
        del request.session['user']
