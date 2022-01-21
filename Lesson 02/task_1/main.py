"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import re


def get_value_regexp(template='', buffer=''):
    data = re.compile(r''+template+'')
    result = data.findall(buffer)
    if len(str(result[0]).split()) > 2:
        return str(result[0]).split()[2].rstrip().lstrip()
    else:
        return str(result[0]).rstrip().lstrip()


def get_data():
    ls_main = []
    ls_hdr = ['Изготовитель системы', 'Windows', 'Код продукта', 'Тип системы']
    ls_prd = []
    ls_wnd = []
    ls_prc = []
    ls_ost = []
    file_list = ['info_1.txt', 'info_2.txt', 'info_3.txt']
    ls_main.append(ls_hdr)
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as fr:
            buffer = fr.read()
            ls_prd.append(get_value_regexp('Изготовитель системы:\s*\S*', buffer))
            ls_wnd.append(get_value_regexp('Windows\s\S*', buffer))
            ls_prc.append(get_value_regexp('Код продукта:\s*\S*', buffer))
            ls_ost.append(get_value_regexp('Тип системы:\s*\S*', buffer))
    for r in range(0, len(ls_hdr)-1):
        line = []
        line.append(ls_prd[r])
        line.append(ls_wnd[r])
        line.append(ls_prc[r])
        line.append(ls_ost[r])
        ls_main.append(line)
    return ls_main


def write_to_csv(file_name = 'main_data'):
    with open(file_name, 'w', encoding='utf-8') as f:
        #file = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        file = csv.writer(f)
        for row in get_data():
            file.writerow(row)


write_to_csv('data_report.csv')