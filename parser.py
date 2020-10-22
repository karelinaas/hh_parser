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

            for tag in sub_tags:
                classes = str(tag.classNames).strip()

                if classes == 'bloko-link HH-LinkModifier':
                    print(i, 'Ссылка:', tag.href)
                    print('Название:', tag.innerText)
                elif classes == 'bloko-section-header-3 bloko-section-header-3_lite' and tag.innerText:
                    print('ЗП:', tag.innerText)
                elif classes == 'vacancy-serp-item__meta-info' and 'vacancy-serp__vacancy-address' in tag.innerHTML:
                    print('Город:', tag.innerHTML)
                    print(tag.innerText)

            print('------------------ page', page)
        page += 1
else:
    exit('Не указан обязательный параметр - URL')
