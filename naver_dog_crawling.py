from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
from datetime import timedelta
import time
import pandas as pd

from connection.engine_factory import EngineFactory

user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 "
              "Safari/537.36")

search_url = "https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query=강아지+예방접종시기"


def configure_browser():
    chrome_options = Options()
    chrome_options.add_argument('user-agent=' + user_agent)
    # 메모리가 부족해서 에러 발생 막음
    chrome_options.add_argument("--disable-dev-shm-usage")
    # 브라우저 꺼짐 방지
    chrome_options.add_experimental_option("detach", True)
    # 브라우저 창 안 띄움
    # chrome_options.add_argument('headless')
    return chrome_options


def click_year(driver, year):
    year_map = {
        '2021': 'li[1]',
        '2022': 'li[2]',
        '2023': 'li[3]'
    }
    xpath = f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div/div/div[1]/div/div/div/ul/{year_map[year]}'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def click_month(driver, month):
    month_map = {
        '01': 'li[1]', '02': 'li[2]', '03': 'li[3]', '04': 'li[4]',
        '05': 'li[5]', '06': 'li[6]', '07': 'li[7]', '08': 'li[8]',
        '09': 'li[9]', '10': 'li[10]', '11': 'li[11]', '12': 'li[12]'
    }
    xpath = f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div/div/ul/{month_map[month]}'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def click_day(driver, day):
    xpath = f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/div/div/div/div/div/div[3]/div/div/div/ul/li[{day}]'
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()


def extract_data_from_table(driver, date):
    data_list = []

    # a 태그의 텍스트를 안전하게 수집하는 함수
    def safe_extract_a_text(tr_idx, td_idx, a_idx):
        try:
            return driver.find_element(By.XPATH,
                                       f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[{tr_idx}]/td[{td_idx}]/a[{a_idx}]').text
        except:
            return None  # 해당 a 태그가 없을 경우 None 반환

    # 기초 또는 추가 정보를 가져오는 함수
    def get_vaccine_type(tr_idx):
        return "O" if tr_idx != 7 else "A"


    # tr[1] 데이터 수집
    date_range = driver.find_element(By.XPATH,
                                     f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[3]').text
    start_date, end_date = [x.strip() for x in date_range.split('~')]

    row_data = [date,
                get_vaccine_type(1),
                driver.find_element(By.XPATH,
                                    f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[1]/td[2]').text,
                start_date,
                end_date]
    a_texts = [safe_extract_a_text(1, 4, a_idx) for a_idx in range(1, 4)]
    row_data.extend(a_texts)

    data_list.append(row_data)

    # tr[2]에서 tr[6]까지 데이터 수집
    for i in range(2, 7):
        date_range = driver.find_element(By.XPATH,
                                         f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[{i}]/td[2]').text
        start_date, end_date = [x.strip() for x in date_range.split('~')]
        row_data = [date,
                    get_vaccine_type(i),
                    driver.find_element(By.XPATH,
                                        f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[{i}]/td[1]').text,
                    start_date,
                    end_date]

        a_texts = [safe_extract_a_text(i, 3, a_idx) for a_idx in range(1, 4)]
        row_data.extend(a_texts)

        data_list.append(row_data)

    # tr[7] 데이터 수집
    date_obj = driver.find_element(By.XPATH,
                                     f'//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[2]/div[2]/div/table/tbody/tr[7]/td[2]').text
    row_data = [date,
                get_vaccine_type(7),
                None,
                date_obj,
                date_obj,
                ]
    a_texts = [safe_extract_a_text(7, 3, a_idx) for a_idx in range(1, 3)]
    row_data.extend(a_texts)

    row_data.append(None)
    data_list.append(row_data)

    return data_list


def get_data(engine, animal):
    service = Service(executable_path=ChromeDriverManager().install())
    chrome_options = configure_browser()
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(search_url)
    except Exception as e:
        print(f"don't connect: {e}")
        return False

    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    delta = timedelta(days=1)

    while start_date <= end_date:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[1]/div/a/span'))
        ).click()

        click_year(driver, str(start_date.year))
        time.sleep(0.5)
        click_month(driver, start_date.strftime('%m'))
        time.sleep(0.5)
        click_day(driver, str(start_date.day))
        time.sleep(0.5)

        calculate_btn_xpath = '//*[@id="main_pack"]/div[2]/div/div/div[2]/div/div/div[2]/div[3]/a[2]'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, calculate_btn_xpath))
        ).click()

        time.sleep(1)

        collected_data = extract_data_from_table(driver, start_date.strftime('%Y-%m-%d'))
        animal_id = pd.read_sql(f"select animal_id from petmate.pm_animal_base where animal_nm = '{animal}' ", con=engine)
        animal_id = animal_id['animal_id'].iloc[0]

        df = pd.DataFrame(collected_data, columns=['vaccin_dt', 'vaccin_div', 'vaccin_round',
                                                   'start_dt', 'end_dt', 'vaccin_ct1', 'vaccin_ct2', 'vaccin_ct3'])
        df.insert(0, 'animal_id', animal_id)
        # print(df)
        df.to_sql('pm_vaccin_info', engine, if_exists='append', index=False)

        start_date += delta

    return True


if __name__ == '__main__':
    engine = EngineFactory.create_engine_DEV_by('petmate')
    animal = '강아지'
    result = get_data(engine, animal)
    if result:
        print("Data collection and saving to DB completed successfully!")
    else:
        print("There was an error.")