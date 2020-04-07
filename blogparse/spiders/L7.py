from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

if __name__ == '__main__':
     b = webdriver.Firefox()
    # driver = webdriver.Chrome(executable_path=ChromeDriverManager("80.0.3987.106").install())
    # driver1 = webdriver.Firefox(executable_path=GeckoDriverManager().install())
     b.get('https://www.avito.ru/surgut')
     print(1)

