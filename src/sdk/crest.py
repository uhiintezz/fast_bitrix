import json
import os
from html import escape
import requests
from config import C_REST_WEB_HOOK_URL, C_REST_CLIENT_SECRET, C_REST_CLIENT_ID

class CRest:
    VERSION = '1.36'
    BATCH_COUNT = 50  # count batch 1 query
    TYPE_TRANSPORT = 'json'  # json or xml

    @staticmethod
    def install_app(request):
        result = {
            'rest_only': True,
            'install': False
        }

        if request.get('event') == 'ONAPPINSTALL' and request.get('auth'):
            auth_data = request['auth']
            result['install'] = CRest.set_app_settings(auth_data, True)
        elif request.get('PLACEMENT') == 'DEFAULT':
            auth_data = {
                'access_token': escape(request.get('AUTH_ID', '')),
                'expires_in': escape(request.get('AUTH_EXPIRES', '')),
                'application_token': escape(request.get('APP_SID', '')),
                'refresh_token': escape(request.get('REFRESH_ID', '')),
                'domain': escape(request.get('DOMAIN', '')),
                'client_endpoint': f"https://{escape(request.get('DOMAIN', ''))}/rest/"
            }
            result['rest_only'] = False
            result['install'] = CRest.set_app_settings(auth_data, True)

        return result
    @staticmethod
    def set_app_settings(settings, is_install=False):
        print('set_app_settings')
        if isinstance(settings, dict):
            print('settings:')
            print(settings)
            old_data = CRest.get_app_settings()
            if not is_install and old_data:
                settings = {**old_data, **settings}
            return CRest.set_setting_data(settings)
        return False

    @staticmethod
    def get_app_settings():
        if C_REST_WEB_HOOK_URL:
            data = {
                'client_endpoint': os.environ['C_REST_WEB_HOOK_URL'],
                'is_web_hook': 'Y'
            }
            return data

        data = CRest.get_setting_data()
        if (
                data.get('client_endpoint')
        ):
            return data

        return False

    @staticmethod
    def get_setting_data():
        data = {}
        data['C_REST_CLIENT_ID'] = os.environ.get('C_REST_CLIENT_ID', C_REST_CLIENT_ID)
        data['C_REST_CLIENT_SECRET'] = os.getenv('C_REST_CLIENT_SECRET', C_REST_CLIENT_SECRET)
        print('data:')
        print(data)
        if os.path.exists('settings.json'):
            print('settings.json')
        with open('settings.json') as f:
            data += json.load(f)
        return data

    @staticmethod
    def set_setting_data(settings):
        print('dump')
        with open('settings.json', 'w') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
        return True

    @staticmethod
    def call(method, params={}):
        post_data = {
            'method': method,
            'params': params
        }

        settings = CRest.get_app_settings()
        if settings:
            if 'C_REST_CURRENT_ENCODING' in os.environ:
                post_data['params'] = CRest.change_encoding(post_data['params'])
            return CRest.call_curl(post_data)
        return {'error': 'no_install_app', 'error_information': 'error install app, pls install local applications'}

    @staticmethod
    def call_curl(params):
        if not CRest.check_curl():
            return {'error': 'error_php_lib_curl', 'error_information': 'need install curl lib'}

        settings = CRest.get_app_settings()
        if settings:
            if params.get('this_auth') == 'Y':
                url = 'https://oauth.bitrix.info/oauth/token/'
            else:
                url = f"{settings['client_endpoint']}{params['method']}.{CRest.TYPE_TRANSPORT}"
                if settings.get('is_web_hook') != 'Y':
                    params['params']['auth'] = settings['access_token']

            try:
                response = requests.post(url, data=params['params'])
                response_data = response.json() if CRest.TYPE_TRANSPORT == 'json' else response.text

                if 'error' in response_data:
                    if response_data['error'] == 'expired_token' and not params.get('this_auth'):
                        return CRest.get_new_auth(params)
                    else:
                        return CRest.handle_error(response_data['error'])

                return response_data
            except Exception as e:
                return {
                    'error': 'exception',
                    'error_exception_code': e.__class__.__name__,
                    'error_information': str(e),
                }
        return {'error': 'no_install_app', 'error_information': 'error install app, pls install local application'}

    @staticmethod
    def check_curl():
        try:
            return requests
        except ImportError:
            return False

    @staticmethod
    def get_new_auth(params):
        settings = CRest.get_app_settings()
        if settings:
            auth_params = {
                'this_auth': 'Y',
                'params': {
                    'client_id': settings['C_REST_CLIENT_ID'],
                    'grant_type': 'refresh_token',
                    'client_secret': settings['C_REST_CLIENT_SECRET'],
                    'refresh_token': settings['refresh_token'],
                }
            }
            new_data = CRest.call_curl(auth_params)
            if 'error' not in new_data:
                CRest.set_app_settings(new_data)
                params['this_auth'] = 'N'
                return CRest.call_curl(params)
        return {}

    @staticmethod
    def handle_error(error):
        error_messages = {
            'expired_token': 'expired token, cant get new auth? Check access oauth server.',
            'invalid_token': 'invalid token, need reinstall application',
            'invalid_grant': 'invalid grant, check out define C_REST_CLIENT_SECRET or C_REST_CLIENT_ID',
            'invalid_client': 'invalid client, check out define C_REST_CLIENT_SECRET or C_REST_CLIENT_ID',
            'QUERY_LIMIT_EXCEEDED': 'Too many requests, maximum 2 query by second',
            'ERROR_METHOD_NOT_FOUND': 'Method not found! You can see the permissions of the application: CRest.call(\'scope\')',
            'NO_AUTH_FOUND': 'Some setup error b24, check in table "b_module_to_module" event "OnRestCheckAuth"',
            'INTERNAL_SERVER_ERROR': 'Server down, try later'
        }
        return {'error': error, 'error_information': error_messages.get(error, 'Unknown error.')}

    @staticmethod
    def change_encoding(data, encoding=True):
        if isinstance(data, dict):
            return {CRest.change_encoding(k, encoding): CRest.change_encoding(v, encoding) for k, v in data.items()}
        elif isinstance(data, list):
            return [CRest.change_encoding(item, encoding) for item in data]
        else:
            if encoding:
                return data.encode('utf-8').decode('utf-8')
            else:
                return data


