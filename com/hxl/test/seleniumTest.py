from selenium import webdriver
from selenium.webdriver.firefox.options import Options

url = 'https://h5.youzan.com/wscshop/feature/Sktopl03Tt?oid=20316873'
options = Options()
options.add_argument('--headless')
# driver = webdriver.PhantomJS()
driver = webdriver.Firefox(options=options)
driver.set_window_size(1200, 10000)
driver.get(url)
for i in range(1, 20000, 1000):
    num = i
    print(num)
    jsCode = "var q=document.documentElement.scrollTop=" + str(num)
    driver.execute_script(jsCode)
    # driver.implicitly_wait(2)
jsCode = "var q=document.documentElement.scrollTop=0"
driver.execute_script(jsCode)
print(driver.page_source)
h = driver.find_elements_by_xpath('//h3')
print(type(h))
for h_el in h:
    print(h_el.text)
# driver.save_screenshot('gdm.png')
driver.close()
driver.quit()
