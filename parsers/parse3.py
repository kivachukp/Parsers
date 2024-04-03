from playwright.sync_api import sync_playwright
import json

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()

    # go to url
    page.goto(f'https://omsk.yapdomik.ru/about', timeout=0)

    cities_base = '/html/body/div[1]/div/header/div[2]/div[1]'
    cities = []
    page.locator(f'xpath={cities_base}/a').click()

    for i in range(1, page.locator(f'xpath={cities_base}/div[2]/a').count() + 1):
        c = page.locator(f'xpath={cities_base}/div[2]/a[{i}]').get_attribute('href')
        cities.append(c)

    rest_arr = []


    def parse():
        page.wait_for_selector('div[class="container container--shops addressList"]')

        ##find button
        for i in range(1, page.locator('xpath=//html/body/div[1]/main/div[3]/ul/li').count() + 1):
            path_to_li = f'xpath=//html/body/div[1]/main/div[3]/ul/li[{i}]'  # last li is enumeration variable of items
            info = dict()

            info["name"] = page.locator('xpath=/html/body/div[1]/div/header/a/img').get_attribute('alt')

            address = ", ".join(
                [page.locator('xpath=/html/body/div[1]/div/header/div[2]/div[1]/a').text_content(),
                 page.locator(path_to_li).text_content()])
            info["address"] = address

            location = [
                page.locator(path_to_li).get_attribute('data-latitude'),
                page.locator(path_to_li).get_attribute('data-longitude')
            ]
            info["location"] = location

            page.locator(path_to_li).click()

            # mb there are more numbers
            info["phones"] = [page.locator('xpath=/html/body/div[1]/div/header/div[2]/div[2]/a').text_content()]

            date_time_base = '/html/body/div[1]/main/div[3]/div[2]/ymaps/ymaps/ymaps/ymaps[6]/ymaps/ymaps/ymaps/ymaps[1]/ymaps[2]/ymaps/ymaps/div'
            count_div = page.locator(f'xpath={date_time_base}').count()
            if count_div == 3:
                arr = [
                    " ".join(
                        [page.locator(f'xpath={date_time_base}[3]/div[1]').text_content(),
                         page.locator(f'xpath={date_time_base}[3]/div[2]').text_content()])
                ]
            elif count_div == 4:
                arr = [
                    " ".join(
                        [page.locator(f'xpath={date_time_base}[3]/div[1]').text_content(),
                         page.locator(f'xpath={date_time_base}[3]/div[2]').text_content()]),
                    " ".join(
                        [page.locator(f'xpath={date_time_base}[4]/div[1]').text_content(),
                         page.locator(f'xpath={date_time_base}[4]/div[2]').text_content()]),
                ]

            info["working_hours"] = arr
            rest_arr.append(info)


    parse()

    for i in range(len(cities)):
        page.goto(f"{cities[i]}/about", timeout=0)
        parse()

    with open(f'yapdomik.json', 'w', encoding='utf-8') as file:
        json.dump(rest_arr, file, indent=2, ensure_ascii=False)