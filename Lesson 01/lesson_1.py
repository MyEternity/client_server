'''
1. Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и содержание
    соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в формат
    Unicode и также проверить тип и содержимое переменных.
2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
    (не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления в
    байтовое и выполнить обратное преобразование (используя методы encode и decode).
5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый
    тип на кириллице.
6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
    Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
'''

import subprocess

import chardet

print('---- Start task 01 ----')
words_u = \
    [
        '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
        '\u0441\u043e\u043a\u0435\u0442',
        '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
    ]
words_h = ['разработка', 'сокет', 'декоратор']

print(words_h)
print(words_u)

for x in range(0, len(words_u)):
    print(f'Type is: {type(words_h[x])}, data: {words_h[x]}')
    print(f'Type is: {type(words_u[x])}, data: {words_u[x]}')
    print(f'Data equal: {words_u[x] == words_h[x]}')

print(' ')
print('---- Start task 02 ----')

words_b = [b'class', b'function', b'method']
for x in range(0, len(words_b)):
    print(f'Type is: {type(words_b[x])}, len: {len(words_b[x])} (original data: {words_b[x]})')

print(' ')
print('---- Start task 03 ----')

words_try = ['attribute', 'класс', 'функция', 'type']
for x in range(0, len(words_try)):
    try:
        print(f'Possible transformation Str ({words_try[x]}) > Byte: ({bytes(words_try[x], "utf-8")})')
    except:
        print(f'Impossible data transformation Str > Byte, data: "{words_try[x]}"')

print(' ')
print('---- Start task 04 ----')

words_transform = ['разработка', 'администрирование', 'protocol', 'standard']
for x in range(0, len(words_transform)):
    s = words_transform[x].encode('utf-8')
    print(f'Encoding: {s} - > Decoding: {s.decode("utf-8")}')

print(' ')
print('---- Start task 05 ----')

ping = subprocess.Popen('ping yandex.ru', stdout=subprocess.PIPE)
for x in ping.stdout:
    dec = chardet.detect(x)
    print(x.decode(dec['encoding']).rstrip())

print(' ')
print('---- Start task 06 ----')


def get_file_enc(file_name='test_file.txt'):
    with open('test_file.txt', 'rb') as f:
        b = f.read()
        dec = chardet.detect(b)
        return dec['encoding']


def convert_file(file_name='test_file.txt', file_name_out='test_file_out.txt'):
    enc = get_file_enc(file_name)
    with open(file_name, 'rb') as f_in:
        data = f_in.read().decode(enc)
    with open(file_name_out, 'w', encoding='utf-8') as f_out:
        f_out.write(data)


convert_file()
with open('test_file_out.txt', 'r', encoding='utf-8') as f:
    print(f.read())
