import requests
from bs4 import BeautifulSoup

# Словник для збереження категорій на ОЛХ ("Назва категорії": "посилання")
global_main_categories = {}

# Функція для отримання основних категорій на ОЛХ
def start():
    global global_main_categories
    url = 'https://www.olx.ua/uk/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    main_categories = {}
    contents = soup.find_all('div', 'maincategories-list clr')
    for content in contents:
        listing_contents = content.find_all('div', 'li fleft')
        for elem in listing_contents:
            listing_content = elem.select_one('.link.parent')
            listing_url = listing_content['href']
            main_categories[listing_content.text.strip()] = listing_url
    global_main_categories = main_categories.copy()
    return main_categories

# Функція для парсинга оголошень на ОЛХ
def parser(text, pages, categorie, sort):
    global global_main_categories
    article_content = []
    articles_content = []

    # Формування URL відповідно до обраної категорії
    if categorie == 'Всі оголошення':
        url_cat = f'https://www.olx.ua/uk/list/q-{text}/'
    else:
        url_cat = f'{global_main_categories.get(categorie)}q-{text}/'

    # Формування URL відповідно до сортування
    if sort == 'Рекомендоване вам':
        sort_url = '&search%5Border%5D=relevance:desc'
    elif sort == 'Найдешевші':
        sort_url = '&search%5Border%5D=filter_float_price:asc'
    elif sort == 'Найдорожчі':
        sort_url = '&search%5Border%5D=filter_float_price:desc'
    elif sort == 'Найновіші':
        sort_url = '&search%5Border%5D=created_at:desc'

    # Перевірка, чи вказана кількість сторінок
    try:
        pages = int(pages)
        is_page = True
    except:
        is_page = False

    # Якщо не вказана кількість сторінок, визначити загальну кількість
    if not is_page:
        list_of_pages = []
        url = url_cat + sort_url
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        count_of_pages = soup.find_all('div', 'css-4mw0p4')
        for i in count_of_pages:
            count_of_page = i.find_all('a', 'css-1mi714g')
            for item in count_of_page:
                list_of_pages.append(int(item.text))
        max_page = max(list_of_pages) + 1
    else:
        max_page = pages + 1

    # Перебір сторінок і парсинг оголошень
    for i in range(1, max_page):
        url = f'{url_cat}?page={i}{sort_url}'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        contents = soup.find_all('a', class_='css-rc5s2u')
        for content in contents:
            article_url = 'https://www.olx.ua' + content['href']
            article = content.select_one('.css-u2ayx9')
            if article:
                article_text = article.select_one('.css-16v5mdi.er34gjf0')
                article_price = article.select_one('.css-10b0gli.er34gjf0')
                if article_price:
                    article_content.append(article_text.text)
                    article_content.append(article_price.text)
                    article_content.append(article_url)
                else:
                    article_content.append(article_text.text)
                    article_content.append("Ціна не вказана")
                    article_content.append(article_url)
                articles_content.append(article_content)
                article_content = []
    return articles_content