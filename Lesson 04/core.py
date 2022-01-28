import datetime
import json
import socket

from jsonschema import validate


class SocketWrapper:

    def __init__(self, server_mode: bool=False):
        self._mode = server_mode
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._jim_decl = self.read_settings('jim')
        try:
            if self._mode:
                self._socket.bind((self.read_settings('listen_address'), self.read_settings('default_port')))
                self._socket.listen(self.read_settings('max_connections'))
        except Exception as E:
            print(f'Ошибка инициализации сокета: {E}')

    @property
    def jim_proto(self):
        return self._jim_decl

    @property
    def wrapped_socket(self):
        return self._socket

    @classmethod
    def read_settings(cls, param):
        try:
            with open('settings.json', 'r') as f:
                data = json.loads(f.read())
                return data[param]
        except:
            return None

    def recv_msg(self, new_socket):
        buffer = new_socket.recv(self.read_settings('max_package_length'))
        try:
            if isinstance(buffer, bytes):
                json_data = json.loads(buffer.decode(self.read_settings('encoding')))
                if isinstance(json_data, dict):
                    return json_data
        except Exception as E:
            print(f'Recieved errored data: {E}')
            return {}

    def response_template(self, code):
        responce_templates = {
            200: {self.jim_proto['response']: 200},
            400: {self.jim_proto['response']: 400, 'error': self.jim_proto['error']},
        }
        return responce_templates[code]

    def send_msg(self, data, client_socket=None):
        data['time'] = datetime.datetime.timestamp(datetime.datetime.now())
        buffer = json.dumps(data).encode(self.read_settings('encoding'))
        if not client_socket:
            self.wrapped_socket.send(buffer)
        else:
            client_socket.send(buffer)


class JIMServer(SocketWrapper):
    def __init__(self):
        super().__init__(server_mode=True)

    def process_income_message(self, msg):
        in_greeting = {"action": "string", "time": "float", "user": {"account_name": "string"}}
        try:
            validate(msg, schema=in_greeting)
            if msg['user']['account_name'] == "Guest" and msg['action'] == self.jim_proto['presence']:
                return self.response_template(200)
        except:
            return self.response_template(400)
        return self.response_template(400)

    def run_server(self):
        while True:
            client, client_address = self.wrapped_socket.accept()
            try:
                msg = self.recv_msg(client)
                print(f'Recieved RAW message: {msg}')
                reply = self.process_income_message(msg)
                self.send_msg(data=reply, client_socket=client)
                print(f'Sent message {reply} to client: {client_address}')
                client.close()
            except Exception as E:
                print(f'Recieved error data: {E}')
                client.close()


class JIMClient(SocketWrapper):
    def __init__(self, account_name='Guest'):
        self._account_name = account_name
        super().__init__(server_mode=False)

    def send_presence(self):
        self._socket.connect((self.read_settings('default_ip_address'), self.read_settings('default_port')))
        self.send_msg(
            {'action': self.jim_proto['presence'], 'time': 0, 'user': {'account_name': self._account_name}})
        try:
            reply = self.recv_msg(self.wrapped_socket)
            print(f'Recieved reply data: {reply}')
        except Exception as E:
            print(f'Unexpected error: {E}')
