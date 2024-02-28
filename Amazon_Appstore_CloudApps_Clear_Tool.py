import sys
import time
import logging
import platform
import importlib
import subprocess
import webbrowser
from datetime import datetime
from selenium import webdriver
from urllib.error import HTTPError
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException, \
    StaleElementReferenceException, NoSuchWindowException


class PackageManager:
    def __init__(self, package_manager, required_packages):
        self.package_manager = package_manager
        self.required_packages = required_packages

    def run_subprocess(self, args):
        try:
            print(f"Opening subprocess: {' '.join(args)}")
            subprocess.run(args, check=True)
            print(f"Subprocess closed successfully: {' '.join(args)}")
        except subprocess.CalledProcessError as error:
            print(f"Subprocess error: {error}")
        except OSError as error:
            print(f"OSError: {error}")

    def manage_package(self, package, action):
        try:
            if action == 'install':
                print(f"Attempting to install {package}...")
                args = [self.package_manager, "pip", "install", package]
            elif action == 'update':
                print(f"Checking for {package} update...")
                args = [self.package_manager, "-m", "pip", "install", "--upgrade", package]
            else:
                return
            self.run_subprocess(args)
        except subprocess.CalledProcessError as error:
            print(f"Subprocess error: {error}")
        except OSError as error:
            print(f"OSError: {error}")

    def check_and_update_package(self, package):
        try:
            module = importlib.import_module(package)
            if hasattr(module, '__version__'):
                current_version = module.__version__
                print(f"Current {package} version:", current_version)
                self.manage_package(package, action='update')
                importlib.reload(module)
                updated_version = module.__version__
                if updated_version != current_version:
                    print(f"{package} has been updated to version:", updated_version)
                else:
                    print(f"{package} is already up to date!\n")
        except ImportError:
            print(f"{package} is not installed.")
            self.manage_package(package, action='install')

    def check_and_update_required_packages(self):
        for package in self.required_packages:
            self.check_and_update_package(package)


class SeleniumDriver:
    def __init__(self, browser, username, password, n=10, headless=True):
        self.username = username
        self.password = password
        self.browser = browser
        self.headless = headless
        self.initialize_driver()
        self.driver.maximize_window()
        self.app_ids = [f"a-autoid-{i}-announce" for i in range(n)]

    def initialize_driver(self):
        browsers = ['firefox', 'edge', 'chrome']
        browser_map = {'firefox': webdriver.Firefox, 'edge': webdriver.Edge, 'chrome': webdriver.Chrome}

        if self.browser in browser_map:
            browsers_type = [self.browser]
        else:
            browsers_type = browsers

        for browser in browsers_type:
            try:
                options = self.get_browser_options(browser)
                if self.headless:
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--start-maximized")
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu')
                self.driver = browser_map.get(browser, getattr(webdriver, browser.capitalize()))(options=options)
                print(f"The {browser.capitalize()} browser has been launched{' in headless mode' if self.headless else ''}...!")
                break
            except WebDriverException as e:
                print(f"Exception while launching {browser.capitalize()} browser: {e}")
        else:
            print("Failed to launch any browser.")
        print("WebDriver and Browser initialization are completed...!\n")

    def get_browser_options(self, browser):
        options = None
        if platform.system() == 'Windows':
            options = webdriver.FirefoxOptions() if browser == 'firefox' else webdriver.EdgeOptions() if browser == 'edge' else webdriver.ChromeOptions()
        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
            options = webdriver.FirefoxOptions() if browser == 'firefox' else webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        return options

    def login(self):
        driver = self.driver
        wait = WebDriverWait(driver, 1)
        captcha_image_xpath = '//*[contains(text(),"Try different image") and @onclick="window.location.reload()"]'
        locator = (By.XPATH, captcha_image_xpath)

        try:
            amazon_url = "https://www.amazon.com/"
            driver.get(amazon_url)
            try:
                captcha_element = wait.until(EC.element_to_be_clickable(locator))
                captcha_element.click()
            except NoSuchElementException as e:
                raise NoSuchElementException("Element not found with locator: {}".format(captcha_image_xpath)) from e
        except Exception as e:
            logging.exception(f"Exception occurred: {str(e)}")
            pass

            url1 = "https://www.amazon.com/gp/site-directory?ref=nav_em_linktree_fail"
            url2 = "https://www.amazon.com/"
            driver.get(url1)
            if driver.current_url == url1:
                driver.get(url2)
                try:
                    captcha_element = wait.until(EC.element_to_be_clickable(locator))
                    captcha_element.click()
                except Exception as e:
                    logging.exception(f"Exception occurred: {str(e)}")
                    pass
        except (WebDriverException, NoSuchElementException, TimeoutException) as e:
            logging.exception(f"Exception occurred: {str(e)}")
            pass

        print(f"Successfully opened: {driver.title}\n")

        try:
            account_sign_locator = "//*[contains(@id, 'nav-link-accountList')]"
            account_sign = (By.XPATH, account_sign_locator)
            user_email_locator = "//*[@type='email' and @id='ap_email' and @name='email']"
            user_email = (By.XPATH, user_email_locator)
            continue_button_locator = "//*[@id='continue' and @type='submit' and contains(@class, 'a-button-input')]"
            continue_button = (By.XPATH, continue_button_locator)
            email_error_locator = "//div[@class='a-box-inner a-alert-container']//h4[@class='a-alert-heading' and text()='There was a problem']"
            email_error_path = (By.XPATH, email_error_locator)
            user_password_locator = "//*[@type='password' and @id='ap_password' and @name='password']"
            user_password = (By.XPATH, user_password_locator)
            submit_signin_locator = "//*[@id='signInSubmit' and @type='submit' and contains(@class, 'a-button-input')]"
            submit_signin = (By.XPATH, submit_signin_locator)
            password_error_locator = "//div[@class='a-box-inner a-alert-container']//h4[@class='a-alert-heading' and text()='There was a problem']"
            password_error_path = (By.XPATH, password_error_locator)
            account_locator = "//*[contains(@id, 'nav-link-accountList')]"
            account_path = (By.XPATH, account_locator)
            your_apps_locator = "//a[contains(@href, 'amazon.com/gp/mas/your-account/myapps') and contains(text(), 'Your apps')]"
            your_apps = (By.XPATH, your_apps_locator)
            wait = WebDriverWait(driver, 10)
            error_wait = WebDriverWait(driver, 1)
            your_apps_page_load = 5

            wait.until(EC.element_to_be_clickable(account_sign)).click()
            wait.until(EC.element_to_be_clickable(user_email)).send_keys(username)
            wait.until(EC.element_to_be_clickable(continue_button)).click()
            try:
                emailError = error_wait.until(EC.presence_of_element_located(email_error_path))
                print(f"{emailError.text}: You've given Incorrect Email address !")
                sys.exit(1)
            except (WebDriverException, NoSuchElementException, TimeoutException) as e:
                logging.exception(f"Exception occurred: {str(e)}")
                pass
            print("Successfully taken Username !")
            wait.until(EC.element_to_be_clickable(user_password)).send_keys(password)
            wait.until(EC.element_to_be_clickable(submit_signin)).click()
            try:
                passwordError = error_wait.until(EC.presence_of_element_located(password_error_path))
                print(f"{passwordError.text}: You've given Incorrect Password !")
                sys.exit(1)
            except (WebDriverException, NoSuchElementException, TimeoutException) as e:
                logging.exception(f"Exception occurred: {str(e)}")
                pass
            print("Successfully taken Password !")
            wait.until(EC.element_to_be_clickable(account_path)).click()
            your_apps_element = wait.until(EC.element_to_be_clickable(your_apps))
            print("Successfully Logged In and navigated into Your account !")
            driver.execute_script("arguments[0].scrollIntoView();", your_apps_element)
            your_apps_element.click()
            print("Successfully navigated into Your Apps !\n")
            print("Apps deleting process started !\n")
            time.sleep(your_apps_page_load)
        except (WebDriverException, NoSuchElementException, TimeoutException) as e:
            logging.error("Exception occurred: %s", str(e))
            pass

    def delete_apps(self):
        driver = self.driver
        action_button_locator = "//*[starts-with(@id, '{}')]"
        delete_button_locator = "//*[@class='a-popover-content']//a[@class='a-link-normal' and normalize-space()='Delete this app']"
        delete_app = (By.XPATH, delete_button_locator)
        confirm_button_locator = "//input[@class='a-button-input' and @type='submit' and @aria-labelledby='primary_button-announce']"
        confirm_delete = (By.XPATH, confirm_button_locator)
        app_name_locator = "//div[contains(@class, 'a-box-inner') and contains(@class, 'a-alert-container')]"
        app_name_display = (By.XPATH, app_name_locator)
        last_deletion_time = time.time()
        wait = WebDriverWait(driver, 20)
        app_delete_reload = 1
        scroll_reload = 3
        max_retries = 3
        wait_time = 4
        counter = 0

        while True:
            try:
                app_deleted = False
                for app_id in self.app_ids:
                    try:
                        button = driver.find_element(By.XPATH, action_button_locator.format(app_id))
                        if button.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView();", button)
                            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'a-modal-scroller')))
                            button.click()
                            delete_button = wait.until(EC.element_to_be_clickable(delete_app))
                            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'a-modal-scroller')))
                            delete_button.click()
                            time.sleep(app_delete_reload)
                            confirm_button = wait.until(EC.element_to_be_clickable(confirm_delete))
                            confirm_button.click()
                            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'a-modal-scroller')))
                            app_name = wait.until(EC.visibility_of_element_located(app_name_display))
                            print(f"Deleting app: {app_name.text}")
                            current_time = datetime.now().strftime('[Date: %Y-%m-%d] & [Time: %I:%M:%S %p]')
                            print(f"Date and Time of deletion: {current_time}")
                            counter += 1
                            print(f"Number of apps deleted: {counter}\n")
                            actions = ActionChains(driver)
                            actions.send_keys(Keys.PAGE_UP).perform()
                            time.sleep(scroll_reload)
                            app_deleted = True
                            last_deletion_time = time.time()
                    except (NoSuchElementException, StaleElementReferenceException, NoSuchWindowException) as e:
                        logging.exception(f"Exception occurred: {str(e)}")
                        pass
                if not app_deleted and time.time() - last_deletion_time > 20:
                    print("There are no apps to delete from the cloud. The execution has stopped.")
                    break
            except (NoSuchElementException, StaleElementReferenceException, NoSuchWindowException) as e:
                logging.exception(f"Exception occurred: {str(e)}")
                pass
            except (HTTPError, TimeoutError, ConnectionError) as e:
                if isinstance(e, HTTPError) and e.code in (400, 404, 500, 502, 503):
                    print(f"{e.code} Error: {e}")
                elif isinstance(e, TimeoutError):
                    print(f"Timeout error occurred: {e}")
                elif isinstance(e, ConnectionError) and ('ERR_INTERNET_DISCONNECTED' in str(e) or 'No internet connection' in str(e)):
                    print(f"Connection error occurred: {e}")
                else:
                    print(f"Unhandled error occurred: {e}")
                for retry_count in range(max_retries):
                    driver.refresh()
                    time.sleep(wait_time)
                else:
                    print("Reached the maximum number of retries. Closing the browser.")
                    driver.quit()
                    break
            except Exception as e:
                print(f"Error occurred: {e}")
                driver.quit()
                raise
        if counter > 0:
            print(f"Total number of apps deleted: {counter}")

    def close_browser(self):
        self.driver.close()


class AmazonAppDeleter:
    def __init__(self, webbrowser, username, password):
        self.selenium_driver = SeleniumDriver(webbrowser, username, password)

    def main_method(self):
        try:
            self.selenium_driver.login()
            self.selenium_driver.delete_apps()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.selenium_driver.close_browser()


if __name__ == "__main__":
    try:
        start_time = time.time()
        if len(sys.argv) < 3:
            raise ValueError("Please provide both username and password as command-line arguments.")
        username = sys.argv[1]
        password = sys.argv[2]
        required_packages = ['pip', 'selenium', 'webdriver_manager']
        package_manager = PackageManager(sys.executable, required_packages)
        package_manager.check_and_update_required_packages()
        logging.basicConfig(filename='app_deleter.log', level=logging.DEBUG,
                            format='%(asctime)s %(levelname)-8s %(message)s')
        print("Launching browser...")
        app_deleter = AmazonAppDeleter(webbrowser, username, password)
        app_deleter.main_method()
        end_time = time.time()
        total_execution_time_seconds = int(end_time - start_time)
        hours, remainder = divmod(total_execution_time_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_execution_time = f"{hours}h:{minutes}min:{seconds}sec"
        print(f"Total Execution Time: {total_execution_time}")
    except Exception as e:
        logging.exception(f"Exception occurred: {str(e)}")
