from playwright.sync_api import sync_playwright
from parsel import Selector
import json

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page()

    # go to url
    page.goto('https://www.santaelena.com.co/tiendas-pasteleria/tienda-medellin/', timeout=0)
    # get HTML
    arr = []
    for i in range(1, page.locator(
            f'xpath=/html/body/header/div/header/div/div/div[2]/div/div/div/div/nav[1]/ul/li[3]/ul/li').count() + 1):
        arr.append(page.locator(
            f'xpath=/html/body/header/div/header/div/div/div[2]/div/div/div/div/nav[1]/ul/li[3]/ul/li[{i}]/a').get_attribute(
            'href'))

    path_to_name = '/div[1]/div/h3'
    path_to_address = '/div[3]/div/div/p[1]'
    path_to_phone = '/div[3]/div/div/p[2]'
    path_to_w_hours_1 = '/div[3]/div/div/p[4]'
    path_to_w_hours_2 = '/div[3]/div/div/p[5]'
    path_to_location = '/div[4]/div/div/a'

    array = []

    for c in range(len(arr)):
        if c == 0:
            city_name = page.locator(
                'xpath=/html/body/div[1]/div/div/section[3]/div/div/div/div/div/div[1]/div/h2').text_content()
            start_value = 4
        else:
            page.goto(arr[c], timeout=0)
            city_name = page.locator(
                'xpath=/html/body/div[1]/div/div/section[2]/div/div/div/div/div/div[1]/div/h2').text_content()
            start_value = 3

        for j in range(start_value, page.locator(f'xpath=/html/body/div[1]/div/div/section').count() - 1):
            path_to_section = f'/html/body/div[1]/div/div/section[{j}]'  # section with [] is enumeration variable of items

            for i in range(1, page.locator(f'xpath={path_to_section}/div/div/div').count() + 1):
                path_to_item = f'/div/div/div[{i}]/div/div'  # div with [] is enumeration variable of items

                info = dict()
                info["name"] = page.locator(
                    f'xpath={path_to_section}{path_to_item}{path_to_name}').text_content().strip().replace("\n",
                                                                                                           " ").replace(
                    "  ", " ")

                address = page.locator(f'xpath={path_to_section}{path_to_item}{path_to_address}').all_inner_texts()[
                    0].replace('\n', ' ')

                try:
                    info["address"] = ", ".join([
                        city_name.split(" ")[-1],
                        address[address.index(":") + 1:].strip()])
                except ValueError:
                    info["address"] = ", ".join([
                        city_name.split(" ")[-1],
                        address.strip()])

                info["location"] = page.locator(
                    f'xpath={path_to_section}{path_to_item}{path_to_location}').get_attribute('href')
                try:
                    number = page.locator(f'xpath={path_to_section}{path_to_item}{path_to_phone}').text_content()
                    info["phone"] = number[number.index(":") + 2:]
                except ValueError:
                    number = page.locator(
                        f'xpath={path_to_section}{path_to_item}{path_to_phone[:-3]}[3]').text_content()
                    info["phone"] = number[number.index(":") + 2:]

                count_hours = page.locator(f'xpath={path_to_section}{path_to_item}/div[3]/div/div/p').count()

                # it will be easier to parse each page separately
                if count_hours == 2:
                    info["phone"] = ''
                    hours = page.locator(
                        f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1[:-3]}[2]').text_content()
                    hours = hours[hours.index(":") + 1:].strip()
                    info["working_hours"] = [hours]
                elif count_hours == 3:
                    info["working_hours"] = [page.locator(
                        f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1[:-3]}[3]').text_content()]
                    if c == 2:
                        info["phone"] = page.locator(
                            f'xpath={path_to_section}{path_to_item}{path_to_phone[:-3]}[2]').text_content()
                        info["working_hours"] = page.locator(
                            f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1[:-3]}[3]').all_inner_texts()[
                            0].split("\n")
                elif count_hours == 4:
                    info["working_hours"] = [
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1}').text_content()]
                    if c == 1:
                        info["working_hours"] = [
                            page.locator(
                                f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1[:-3]}[3]').text_content(),
                            page.locator(
                                f'xpath={path_to_section}{path_to_item}{path_to_w_hours_2[:-3]}[4]').text_content()
                        ]
                elif count_hours == 5:
                    info["working_hours"] = [
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1}').text_content(),
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_w_hours_2}').text_content()
                    ]
                elif count_hours == 6:
                    address = " ".join([
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_address}').text_content(),
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_address[:-3]}[2]').text_content()
                    ])
                    info["address"] = ", ".join([
                        city_name.split(" ")[-1],
                        address[address.index(":") + 1:].strip()])
                    info["working_hours"] = [
                        page.locator(
                            f'xpath={path_to_section}{path_to_item}{path_to_w_hours_1[:-3]}[5]').text_content(),
                        page.locator(f'xpath={path_to_section}{path_to_item}{path_to_w_hours_2[:-3]}[6]').text_content()
                    ]

                array.append(info)
    data = []
    with sync_playwright() as plays:
        browser = plays.firefox.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        for i in range(len(data)):
            url = data[i]['location']

            page.goto(url)
            page.wait_for_timeout(5000)
            link = page.url
            page.wait_for_timeout(300)
            reg = ['!1d(-?\d+(?:\.\d+)?)!2d(-?\d+(?:\.\d+))', '!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+))']

            match = re.search(reg[0], link)
            if match:
                pass
            else:
                match = re.search(reg[1], link)
            text = match[0]

            if text[:3] == '!1d':
                temp = text.split('!2d')
                new_text = [temp[1], temp[0][3:]]
            elif text[:3] == '!3d':
                temp = text.split('!4d')
                new_text = [temp[0][3:], temp[1]]

            data[i]['location'] = new_text

    with open(f'santaelena.json', 'w', encoding='utf-8') as file:
        json.dump(array, file, indent=2, ensure_ascii=False)