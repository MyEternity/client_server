"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""

import yaml


def write_yaml_data(file_name='file.yaml', data={}):
    with open(file_name, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def read_yaml_data(file_name='file.yaml'):
    with open(file_name, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


w_dct = {'greetings': ['Привет', 'Ку', 'Хай ©', 'Дарова!'],
         'age': 18,
         'metrics': {'work_name': 'Компания®',
                     'school_name': 'Школа №116'
                     }
         }

write_yaml_data('file.yaml', w_dct)
r_dct = read_yaml_data()
if w_dct == r_dct:
    print('Данные совпадают!')
else:
    print('Данные различаются!')
