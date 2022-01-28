import json
import unittest

import core


class SocketWrapperDemoSocket:

    def recv_msg(self, buffer):
        try:
            if isinstance(buffer, bytes):
                json_data = json.loads(buffer.decode('utf-8'))
                if isinstance(json_data, dict):
                    return json_data
        except Exception as E:
            print(f'Recieved errored data: {E}')
            return {}

    def send_msg(self, data):
        data['time'] = 1.1
        buffer = json.dumps(data).encode('utf-8')
        return buffer


class TestSocketWrapper(unittest.TestCase):

    def test_read_settings(self):
        # Проверяем чтение файла настроек.
        cls = core.SocketWrapper()
        test = cls.read_settings('encoding')
        self.assertEqual(test, 'utf-8')

    def test_recv_msg_01(self):
        # Проверяем приходящие в сокет типы данных.
        cls = SocketWrapperDemoSocket()
        dict_ = '{"action": "presense", "time": "1.1", "user": {"account_name": "Guest"}}'
        byte_ = dict_.encode('utf-8')
        self.assertEqual(cls.recv_msg(byte_), json.loads(dict_))

    def test_recv_msg_02(self):
        # Проверяем приходящие в сокет типы данных.
        cls = SocketWrapperDemoSocket()
        dict_ = {"action": "presense", "time": "1.1", "user": {"account_name": "Guest"}}
        byte_ = str(dict_).encode('utf-8')
        self.assertEqual(cls.recv_msg(byte_), json.loads('{}'))

    def test_snd_msg_01(self):
        # Проверяем исходящий в сокет тип данных
        cls = SocketWrapperDemoSocket()
        dict_ = {"action": "presense", "time": "1.1", "user": {"account_name": "Guest"}}
        self.assertTrue(isinstance(cls.send_msg(dict_), bytes))

    def test_response_template_200(self):
        # Проверяем шаблон 200
        cls = core.SocketWrapper()
        t1 = cls.response_template(200)
        self.assertEqual(t1, {'response': 200})

    def test_response_template_400(self):
        # Проверяем шаблон 400
        cls = core.SocketWrapper()
        t1 = cls.response_template(400)
        self.assertEqual(t1, {'response': 400, 'error': 'error'})

    def test_response_template_300(self):
        # Проверяем шаблон 300 - у нас заглушка вернет 400
        cls = core.SocketWrapper()
        t1 = cls.response_template(400)
        self.assertEqual(t1, {'response': 400, 'error': 'error'})

    def test_jimserver_process_income_message_01(self):
        # Сервер валидирует схему и состав привествия - здесь опечатка в presence.
        cls = core.JIMServer()
        data = cls.process_income_message({"action": "presense", "time": "1.1", "user": {"account_name": "Guest"}})
        self.assertEqual(data, {'error': 'error', 'response': 400})

    def test_jimserver_process_income_message_02(self):
        # Корректное сообщение приветствия серверу.
        cls = core.JIMServer()
        data = cls.process_income_message({"action": "presence", "time": "1.1", "user": {"account_name": "Guest"}})
        self.assertEqual(data, {'response': 200})

    def test_jimserver_process_income_message_03(self):
        # А это не пройдет валидацию по схеме json
        cls = core.JIMServer()
        data = cls.process_income_message({"action": "presence", "time": "1.1"})
        self.assertEqual(data, {'error': 'error', 'response': 400})
