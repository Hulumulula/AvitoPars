from selenium import webdriver
from fake_useragent import UserAgent
import json
import datetime
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import pytesseract
from PIL import Image
import base64

# The path to pyTesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Config to Tesseract
custom_config = r"--oem 3 --psm 13"

# Url
url = "https://www.avito.ru/sankt-peterburg/kvartiry/sdam/na_dlitelnyy_srok-ASgBAgICAkSSA8gQ8AeQUg"

# options
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={UserAgent().random}")

# Disable webdriver mode
# for older ChromeDriver under version 79.0.3945.16
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# for ChromeDriver version 79.0.3945.16 or ever
options.add_argument("--disable-blink-features=AutomationControlled")

# headless mode
options.add_argument("--headless")


driver = webdriver.Chrome(
    executable_path=r"C:\Users\Александр\Desktop\ProjectNFT\pythonProject\chromedriver.exe",
    options=options
)

currencies = {
    "₽": "RUB",
    "$": "USD",
    "€": "EUR"
}

try:
    driver.get(url=url)
    time_to_wait = 20
    time_out = 5
    driver.implicitly_wait(time_to_wait)

    # Get the number of pages
    all_page = driver.find_element_by_xpath("//div[@data-marker='pagination-button']")
    span_page = all_page.find_elements_by_xpath("./span")
    page = int(span_page[-2].text)

    # Go through the pages
    for i in range(1, page - 1):

        # Date
        cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")

        # List of data
        data_product = []

        # Csv module
        with open(f"Avito_{cur_time}_page_{i}.csv", "w", encoding='utf-8') as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    "Ссылка на товар",
                    "Название",
                    "Время публикации",
                    "Оплата",
                    "Валюта",
                    "Дополнительная оплата",
                    "Имя продавца",
                    "Ссылка на продавца",
                    "Номер телефона",
                    "Ссылки на фотографии товара",
                    "Описание товара",
                    "Расположение"
                )
            )

        # Getting all the elements on the page
        items = driver.find_elements_by_xpath("//h3[@itemprop='name']")

        # Go to the information block
        for item in items:

            # Open the block and go to its window
            item.click()
            driver.switch_to.window(driver.window_handles[1])
            images = []

            # Working link
            current_url = driver.current_url
            print(current_url)

            # We get the information we need
            try:
                element_present = ec.presence_of_element_located((By.XPATH, "//*[@class='title-info-title-text']"))
                title_text = WebDriverWait(driver, time_out).until(element_present)
                print(f"Название = {title_text.text}")

                element_present = ec.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class, 'title-info-metadata-item-redesign')]"
                ))
                publication_time = WebDriverWait(driver, time_out).until(element_present)
                print(f"Время публикации = {publication_time.text}")

                element_present = ec.presence_of_element_located((By.XPATH, "//span[@itemprop='price']"))
                money_per_month = WebDriverWait(driver, time_out).until(element_present)
                print(f"Оплата в месяц = {money_per_month.text}")

                element_present = ec.presence_of_element_located((By.XPATH, "./.."))
                currency = "RUB"
                for j in WebDriverWait(money_per_month, time_out).until(element_present).text:
                    if j in currencies:
                        currency = j[0]
                        print(f"Валюта = {currency}")
                        break

                element_present = ec.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class, 'item-price-sub-price')]"
                ))
                deposit = WebDriverWait(driver, time_out).until(element_present)
                print(f"Залог = {deposit.text}")

                element_present = ec.presence_of_element_located((By.XPATH, "//div[@data-marker='seller-info/name']"))
                username = WebDriverWait(driver, time_out).until(element_present)
                print(f"Имя продавца = {username.text}")

                element_present = ec.presence_of_element_located((By.XPATH, "//div[@data-marker='seller-info/name']/a"))
                username_link = WebDriverWait(driver, time_out).until(element_present)
                username_link = username_link.get_attribute('href')
                print(f"Ссылка на продавца = {username_link}")

                element_present = ec.presence_of_all_elements_located((
                    By.XPATH,
                    "//div[@class='gallery-list-item-link']"
                ))
                images_div = WebDriverWait(driver, time_out).until(element_present)
                for image_div in images_div:
                    image = image_div.find_element_by_xpath(".//img").get_attribute('src')
                    images.append(image)
                print("Список ссылок на все прилагаемые фотографии: ", images)

                description = driver.find_element_by_xpath("//div[@itemprop='description']")
                print("Описание товара = ", description.text)

                geolocation = driver.find_element_by_xpath("//div[@itemprop='address']/span")
                print(f"Расположение = {geolocation.text}")

                # Get to phone number
                element_present = ec.presence_of_element_located((
                    By.XPATH,
                    "//*[@data-marker='item-phone-button/card']"
                ))
                button_phone = WebDriverWait(driver, time_out).until(element_present)
                button_phone.click()

                # all_html_page = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
                # print(all_html_page)

                element_present = ec.presence_of_element_located((
                    By.XPATH,
                    "//*[@data-marker='phone-popup/phone-image']"
                ))
                number_photo = WebDriverWait(driver, time_out).until(element_present)
                src = number_photo.get_attribute("src")
                img_str = src.split(',')[1]
                img_data = base64.b64decode(img_str)

                with open("photo.png", "wb") as file:
                    file.write(img_data)

                img = Image.open("photo.png")
                number = pytesseract.image_to_string(img, config=custom_config)
                print(f"Номер телефона = {number}")

                data_product.append(
                    {
                        "current_url": current_url,
                        "title_text": title_text.text,
                        "publication_time": publication_time.text,
                        "money_per_month": money_per_month.text,
                        "currency": currency,
                        "deposit": deposit.text,
                        "username": username.text,
                        "username_link": username_link,
                        "number": number,
                        "images": images,
                        "description": description.text,
                        "geolocation": geolocation.text
                    }
                )

                # Save to a csv file
                with open(f"Avito_{cur_time}_page_{i}.csv", "a", encoding='utf-8') as file:
                    writer = csv.writer(file)

                    writer.writerow(
                        (
                            current_url,
                            title_text.text,
                            publication_time.text,
                            money_per_month.text,
                            currency,
                            deposit.text,
                            username.text,
                            username_link,
                            number,
                            images,
                            description.text,
                            geolocation.text
                        )
                    )
            except TimeoutException:
                print("Timed out waiting for page to load")

            # Close the window and return to the main page
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Save to a json file
        with open(f"Avito_{cur_time}_page_{i}.json", "w") as file:
            json.dump(data_product, file, indent=4, ensure_ascii=False)

        # Go to the next page
        driver.find_element_by_xpath("//span[@data-marker='pagination-button/next']").click()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

except Exception as ex:
    print(ex)

finally:
    driver.close()
    driver.quit()
