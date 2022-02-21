import time

import selenium
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1680,1080')
browser = selenium.webdriver.Chrome(options=options)
browser.delete_all_cookies()


def main():
    browser.get('https://www.mlb.com/player/shohei-ohtani-660271')

    # <section class="statistics"> に含まれる <button data-type="hitting"> ボタンをクリック
    button = filter_elements(
        browser.find_elements_by_xpath("//button[@data-type='hitting']"),
        'class',
        'statistics'
    )
    browser.execute_script('arguments[0].click();', button)
    time.sleep(3)   # 描画を3秒間待ちます

    # <div id="careerTable"> に含まれる <td class="col-10.row-x"> を標準出力
    scopes = [
        {'year': '2021', 'row': 'row-3'},
    ]
#    scopes = [
#        {'year': '2018', 'row': 'row-0'},
#        {'year': '2019', 'row': 'row-1'},
#        {'year': '2020', 'row': 'row-2'},
#        {'year': '2021', 'row': 'row-3'},
#    ]
    for scope in scopes:
        stats = filter_elements(
            browser.find_elements_by_class_name("col-10.%s" % scope['row']),
            'id',
            'careerTable'
        )
#        print("%s: %s" % (scope['year'], stats.text))
        print(stats.text)

    # ブラウザの終了
    browser.close()
    browser.quit()


def filter_elements(elements, parent_key, parent_value):
    for element in elements:
        path = './..'

        while True:
            target = element.find_element_by_xpath(path)
            if target.tag_name == 'html':
                break
            elif target.get_attribute(parent_key) == parent_value:
                return element
            else:
                path += '/..'

    return None


if __name__ == "__main__":
    main()
