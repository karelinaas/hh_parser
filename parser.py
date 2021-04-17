import csv
import re
import sys
import time

import AdvancedHTMLParser
import mechanize


if len(sys.argv) > 1:
    to_csv = []

    # имитация браузера (т.к. HH блочит запросы не из браузера)
    br = mechanize.Browser()
    # html-парсер
    parser = AdvancedHTMLParser.AdvancedHTMLParser()

    page = 1

    # на всякий случай оборачиваю в try, т.к. ошибок может быть много разных
    # так хоть что-то попадёт в csv
    try:
        while page <= 3:  # hh даёт посмотреть максимум 40 страниц, сколько бы не было вакансий
            if page > 1:
                # проход по пагинации (тык по ссылке на след. страницу)
                html_str = br.follow_link(text=str(page)).read()
            else:
                # открытие в "браузере" стартового url-а
                html_str = br.open(sys.argv[1]).read()

            # скармливаем парсеру то, что получили "браузером"
            parser.parseStr(html_str.decode('UTF-8'))

            # парсим карточки вакансий по аттрибуту class
            vacancies = parser.getElementsByClassName('vacancy-serp-item')

            for i, vac_tag in enumerate(vacancies):
                data_found = False

                # получаем все дочерние тэги карточки
                sub_tags = vac_tag.getAllChildNodes()

                vacancy_info = {
                    'link': '',
                    'name': '',
                    'salary': '',
                    'city': '',
                }

                for tag in sub_tags:
                    # когда всё уже нашли, хватит перебирать
                    if vacancy_info['link'] and vacancy_info['name'] and vacancy_info['salary'] and vacancy_info['city']:
                        data_found = True
                        to_csv.append(vacancy_info)
                        break

                    classes = str(tag.classNames).strip()
                    attr_dict = tag.attributesDict

                    # по аттрибуту class (и др.) находим:
                    if classes == 'bloko-link' and attr_dict and 'data-qa' in attr_dict and \
                            str(attr_dict['data-qa']).strip() == 'vacancy-serp__vacancy-title':
                        # ссылка и название вакансии
                        vacancy_info['link'] = tag.href
                        vacancy_info['name'] = tag.innerText
                    elif classes == 'bloko-section-header-3 bloko-section-header-3_lite' and tag.innerText:
                        # зарплата
                        vacancy_info['salary'] = re.sub('<[^<]+?>', '', tag.innerHTML)
                    elif classes == 'vacancy-serp-item__meta-info' and 'vacancy-serp__vacancy-address' in tag.innerHTML:
                        # город (тут приходится резать тэги)
                        vacancy_info['city'] = re.sub('<[^<]+?>', '', tag.innerHTML)

                if not data_found:
                    to_csv.append(vacancy_info)

            print('---------------- спарсили страницу', page, '(макс. 40)')
            page += 1
    except Exception:
        pass
    finally:
        print('Удалось обработать', page - 1, 'страниц, сохраняем csv...')

        keys = to_csv[0].keys()
        with open('vacancies_' + str(time.time()) + '.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(to_csv)
else:
    exit('Не указан обязательный параметр - URL')
