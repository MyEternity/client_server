import datetime
import json
import select
import socket
import sys

from jsonschema import validate

from logs import Log


def ext_logger(fn):
    def wrapper(*args, **kwargs):
        print(f' {datetime.datetime.now()} -[EXT_LOGGER]: {fn.__name__}({args, kwargs})')
        return fn(*args, **kwargs)

    return wrapper


class SocketWrapper:
    def __init__(self, server_mode: int):
        self._mode = server_mode
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._jim_decl = self.read_settings('jim')
        self._connected = True
        try:
            if self._mode:
                self._log = Log(file_name='tcp_server.log', rotate_daily=True).get_logger
                self._socket.settimeout(self.read_settings('timeout'))
                self._socket.bind((self.read_settings('listen_address'), self.read_settings('default_port')))
                self._socket.listen(self.read_settings('max_connections'))
                self.log.debug(f'Инициализация обертки сервера: {self._socket}')
            else:
                self._log = Log('tcp_client.log').get_logger
                self._socket.connect((self.read_settings('default_ip_address'), self.read_settings('default_port')))
                self.log.debug(f'Инициализация обертки клиента: {self._socket}')
        except Exception as E:
            self._connected = False
            self.log.error(f'Ошибка инициализации обертки: {E}')

    @property
    def log(self):
        return self._log

    @property
    def connected(self):
        return self._connected

    @property
    def jim_proto(self):
        return self._jim_decl

    @property
    def wrapped_socket(self):
        return self._socket

    @classmethod
    @ext_logger
    def read_settings(cls, param):
        try:
            with open('settings.json', 'r') as f:
                data = json.loads(f.read())
                return data[param]
        except:
            return None

    @ext_logger
    def recv_msg(self, new_socket):
        buffer = new_socket.recv(self.read_settings('max_package_length'))
        try:
            if isinstance(buffer, bytes):
                self.log.debug(f'Получены данные от {new_socket}, байт: {len(buffer)}')
                json_data = json.loads(buffer.decode(self.read_settings('encoding')))
                if isinstance(json_data, dict):
                    self.log.debug(f'Содержимое буффера: {json_data}')
                    return json_data
        except Exception as E:
            self.log.error(f'Ошибка: {E}')
            return {}

    @ext_logger
    def response_template(self, code):
        responce_templates = {
            200: {self.jim_proto['response']: 200},
            400: {self.jim_proto['response']: 400, 'error': self.jim_proto['error']},
        }
        return responce_templates[code]

    @ext_logger
    def send_msg(self, data, client_socket=None):
        data['time'] = datetime.datetime.timestamp(datetime.datetime.now())
        buffer = json.dumps(data).encode(self.read_settings('encoding'))
        if not client_socket:
            self.log.debug(f'Отправка данных: {data} на сокет: {self.wrapped_socket}')
            self.wrapped_socket.send(buffer)
        else:
            self.log.debug(f'Отправка данных: {data} на сокет: {client_socket}')
            client_socket.send(buffer)


class JIMServer(SocketWrapper):
    def __init__(self):
        super().__init__(server_mode=True)
        self.log.info(f'Запуск модуля сервера.')


    @ext_logger
    def process_income_message(self, msg):
        in_greeting = {"action": "string", "time": "float", "user": {"account_name": "string"}}
        in_message = {"action": "string", "message": "string", "time": "float", "user": {"account_name": "string"}}
        try:
            try:
                validate(msg, schema=in_greeting)
                if msg['user']['account_name'] == "Guest" and msg['action'] == self.jim_proto['presence']:
                    return self.response_template(200)
            except:
                pass
            try:
                validate(msg, schema=in_message)
                if msg['user']['account_name'] == "Guest" and msg['action'] == "message":
                    return self.response_template(200)
            except:
                pass
        except:
            return self.response_template(400)
        return self.response_template(400)

    @ext_logger
    def run_server(self):
        inputs = [self.wrapped_socket]
        self.outputs = []

        while True:
            try:
                _input, _output, _except = select.select(inputs, self.outputs, [])
            except select.error:
                break

            for s in _input:
                try:
                    if s == self.wrapped_socket:
                        client, client_address = self.wrapped_socket.accept()
                        self.log.info(f'Клиент: {client.fileno(), client_address} подключился.')
                        msg = self.recv_msg(client)
                        reply = self.process_income_message(msg)

                        inputs.append(client)
                        self.outputs.append(client)

                        for o in self.outputs:
                            self.send_msg({'action': 'message', 'message': 'new client!', 'time': 0, 'user': {'account_name': 'Guest'}}, o)

                    else:
                        msg = self.recv_msg(s)
                        reply = self.process_income_message(msg)
                        for o in self.outputs:
                            if dict(msg).get('message', None) is not None:
                                self.send_msg(msg, o)
                            else:
                                if o != s:
                                    self.send_msg(data=reply, client_socket=o)


                except socket.error as E:
                    self.log.error(f'Данные получены с ошибкой: {E}')
                    inputs.remove(s)
                    self.outputs.remove(s)



class JIMClient(SocketWrapper):
    def __init__(self, account_name='Guest'):
        self.flag = False
        self._account_name = account_name
        super().__init__(server_mode=False)
        self.log.info(f'Запуск модуля клиента.')

    @ext_logger
    def send_presence(self):
        if self.connected:
            self.send_msg(
                {'action': self.jim_proto['presence'], 'time': 0, 'user': {'account_name': self._account_name}})
            try:
                reply = self.recv_msg(self.wrapped_socket)
                self.log.info(f'Принято сообщение от сервера: {reply}')
            except Exception as E:
                self.log.error(f'Данные получены с ошибкой: {E}')
        else:
            self.log.warn(f'Нет подключения к серверу.')

    def run(self):
        self.send_presence()
        sys.stdout.flush()
        data = input('Введите сообщение: ')
        if data:
            self.send_msg(
                {'action': 'message', 'message': data, 'time': 0, 'user': {'account_name': self._account_name}},
                self.wrapped_socket)

        while not self.flag:
            try:
                _input, _output, _except = select.select([self.wrapped_socket], [], [])
                for i in _input:
                    if i == self.wrapped_socket:
                        data = self.recv_msg(self.wrapped_socket)
                        sys.stdout.write(str(data))
                        sys.stdout.flush()

            except KeyboardInterrupt:
                self.wrapped_socket.close()
                break
