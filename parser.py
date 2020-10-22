import re
import sys

import AdvancedHTMLParser
import mechanize


if len(sys.argv) > 1:
    br = mechanize.Browser()
    url = sys.argv[1]
    page = 1

    while page <= 40:
        if page > 1:
            html_str = br.follow_link(text=str(page)).read()
        else:
            html_str = br.open(url).read()

        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(html_str.decode('UTF-8'))

        vacancies = parser.getElementsByClassName('vacancy-serp-item')

        for i, vac_tag in enumerate(vacancies):
            sub_tags = vac_tag.getAllChildNodes()

            vacancy_info = {
                'link': '',
                'name': '',
                'salary': '',
                'city': '',
            }

            for tag in sub_tags:
                if vacancy_info['link'] and vacancy_info['name'] and vacancy_info['salary'] and vacancy_info['city']:
                    break

                classes = str(tag.classNames).strip()

                if classes == 'bloko-link HH-LinkModifier':
                    vacancy_info['link'] = tag.href
                    vacancy_info['name'] = tag.innerText
                elif classes == 'bloko-section-header-3 bloko-section-header-3_lite' and tag.innerText:
                    vacancy_info['salary'] = tag.innerText
                elif classes == 'vacancy-serp-item__meta-info' and 'vacancy-serp__vacancy-address' in tag.innerHTML:
                    vacancy_info['city'] = re.sub('<[^<]+?>', '', tag.innerHTML)

            print(vacancy_info)
        print('------------------ page', page)
        page += 1
else:
    exit('Не указан обязательный параметр - URL')
