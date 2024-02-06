import argparse
import time
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException



logging.basicConfig(filename='log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

class bot:

    def set_window_position_safely(self, x, y):
        try:
            self.driver.set_window_position(x, y)
        except Exception as e:
            print(f"An error occurred while setting window position: {e}")

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.google.com/")
        self.set_window_position_safely(2000, 0)
        self.driver.maximize_window()

    def login(self, user, passw):
        try:
            time.sleep(3)
            self.driver.get("https://student.iclicker.com/#/login")
            tmp = WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "federationList")))
            dropdown = Select(tmp)
            dropdown.select_by_visible_text("") # put your school's name here, capitals matter
            time.sleep(0.5)
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[2]/div/div/main/div[4]/div[3]/div/button"))).click()
            WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(user)
            WebDriverWait( self.driver, 15).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(passw)
            WebDriverWait( self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@type, 'submit')]"))).click()
            self.driver.get(self.driver.current_url)
            time.sleep(1)
        except TimeoutException as te:
            logging.info(f"TimeoutException: {te}")
            exit(1)
        except NoSuchElementException as nse:
            logging.info(f"NoSuchElementException: {nse}")
            exit(1)
        except Exception as e:
            logging.info(f"An unexpected error occurred: {e}")
            exit(1)

    def refresh_location(self, latitude, longitude):
        time.sleep(5)
        self.set_geolocation(0, 0)
        self.print_current_location()
        time.sleep(5)
        self.set_geolocation(latitude, longitude)
        self.print_current_location()

    def set_geolocation(self, latitude, longitude):
        script = f"""
        navigator.geolocation.getCurrentPosition = function(success) {{
            var position = {{coords: {{latitude:{latitude}, longitude:{longitude}}}}};
            if (success) {{
                success(position);
            }}
        }};
        """
        self.driver.execute_script(script)

    def get_current_location(self):
        script = """
        function getCurrentPosition() {
            return new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(
                    position => resolve(position.coords),
                    error => reject(error)
                );
            });
        }

        return getCurrentPosition();
        """
        return self.driver.execute_script(script)

    def print_current_location(self):
        location = self.get_current_location()
        latitude = location.get('latitude', None)
        longitude = location.get('longitude', None)
        print(f"Current location: Latitude {latitude}, Longitude {longitude}")

    def execute_program(self, title, latitude=None, longitude=None):
        # click into the class
        try:
            WebDriverWait(self.driver, 4).until(EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{title}')]"))).click()
        except TimeoutException:
            logging.info(f"Could not find course with title {title}")
            exit(1)

        # change the location of the user if specified
        if latitude is not None and longitude is not None:
            try:
                self.refresh_location(latitude, longitude)
            except Exception as e:
                logging.info(f"There was an error while changing the location: {e}")
                exit(1)

        # click the join class button
        try:
            WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, f"//button[contains(text(), 'Join')]"))).click()
        except TimeoutError:
            logging.info(f"There was an error while joining the class: {e}")
            exit(1)
        time.sleep(3)
        logging.info(f"Successful run, verify attendance was updated.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description of your script.")

    parser.add_argument("username", help="Username for login")
    parser.add_argument("password", help="Password for login")
    parser.add_argument("course_name", help="Name of the course")

    parser.add_argument("-lat", "--latitude", type=float, help="Latitude")
    parser.add_argument("-long", "--longitude", type=float, help="Longitude")

    args = parser.parse_args()

    tbot = bot()

    tbot.login(args.username, args.password)

    tbot.execute_program(args.course_name, args.latitude, args.longitude)