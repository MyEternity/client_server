import json
import socket
import datetime, time

class SocketWrapper():

    def __init__(self, server_mode: int):
        self._mode = server_mode
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._mode:
                self._socket.bind((self.read_settings('listen_address'), self.read_settings('default_port')))
                self._socket.listen(self.read_settings('max_connections'))
            else:
                self._socket.connect((self.read_settings('default_ip_address'), self.read_settings('default_port')))
        except Exception as E:
            print(f'Ошибка инициализации сокета: {E}')

    @property
    def socket(self):
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

    def send_msg(self, data):
        data['time'] = datetime.datetime.timestamp(datetime.datetime.now())
        buffer = json.dumps(data).encode(self.read_settings('encoding'))
        self._socket.send(buffer)


class JIMServer(SocketWrapper):
    def __init__(self):
        super().__init__(server_mode=True)


class JIMClient(SocketWrapper):
    def __init__(self, account_name='Guest'):
        self._account_name = account_name
        super().__init__(server_mode=False)

    def send_presence(self):
        self.send_msg({'action': 'presence', 'time': 0, 'user': {'account_name': self._account_name}})
