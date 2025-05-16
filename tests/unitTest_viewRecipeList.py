import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class ll_ATS(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_ll(self):

        driver = self.driver
        driver.maximize_window()
        user = "TestSuper"
        pwd = "SnapbackPickleball97!?"
        driver.get("http://127.0.0.1:8000/admin")
        elem = driver.find_element(By.ID,"id_username")
        elem.send_keys(user)
        elem = driver.find_element(By.ID,"id_password")
        elem.send_keys(pwd)
        time.sleep(3)
        elem.send_keys(Keys.RETURN)
        time.sleep(3)
        driver.get("http://127.0.0.1:8000")
        time.sleep(3)
        driver.find_element(By.XPATH, "//a[contains(., 'All
Recipes')]").click()

        time.sleep(5)
        try:
            # verify recipe list exists after selecting button
            # db must contain at least 1 recipe to succeed
            elem = driver.find_element(By.LINK_TEXT, 'View Recipe List')
            self.driver.close()
            assert True

        except NoSuchElementException:
            driver.close()
            self.fail("Recipe List does not appear when All Recipes button is clicked")
            assert False

        time.sleep(3)

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()


