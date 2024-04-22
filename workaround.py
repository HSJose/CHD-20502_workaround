from appium import webdriver
from appium.options.android import UiAutomator2Options
from time import sleep
from  datetime import datetime
import traceback
import concurrent.futures
from dotenv import load_dotenv
from os import getenv

# Load the environment variables
load_dotenv()
api_key = getenv('API_KEY')

# Commenting out all unneccessary capabilities these should not be added but are present in the set of capabilities in the ticket
# The tests are stable when using the recommended set of capabilities
# Issues arise when using the capabilities as presented in the ticekt by client
caps = {
    "deviceName":"Fire Tab",
    "automationName":"UIAutomator2",
    "platformName":"Android",
    # "app":"997f4421-8daa-4c93-92ed-b0c567cf9043",
    # "appPackage":"com.hbo.hbonow",
    # "appActivity":"com.wbd.stream.MainActivity",
    "newCommandTimeout":500,
    "autoAcceptAlerts":False,
    "headspin:capture.video":True,
    "headspin:selector":"device_skus:\"Fire HD Tab\"",
    "headspin:network.regionalRouting":"us-east-1",
    "headspin:app.id":"997f4421-8daa-4c93-92ed-b0c567cf9043",
    # "headspin:capture":"False",
    "headspin:capture.disableHttp2":True,
    # "headspin:controlLock":False,
    # "noReset":False,
    "headspin:language":"en",
    "headspin:retryNewSessionFailure":False,
    "headspin:waitForDeviceOnlineTimeout":600,
    "vendor":"headspin",
    "headspinToken":"6793fe243f4248f594336259a3201c2b"
}

# Converting the capabilities to options 
test_options = UiAutomator2Options().load_capabilities(caps=caps)

# Load balancer WD endpoint
wd_enpoint = f'https://appium-dev.headspin.io:443/v0/{api_key}/wd/hub'


# Wrapping the driver start in a simple retry loop has been shown to be effective in stabilizing the test starts
def test()->str:
    driver = None
    session_id = None
    attempts = 3
    for attempt in range(attempts):
        try:
            driver = webdriver.Remote(
                command_executor=wd_enpoint, 
                options=test_options
            )
            session_id = driver.session_id
            break
        except:
            print(f'Error Message Captured: {datetime.now()}', file=open('error.log', 'a'))
            traceback.print_exc(file=open('error.log', 'a'))
            if attempt < attempts:
                print(f'Retrying attempt {attempt + 1}')
                sleep(5)
            continue
        finally:
            if driver:
                driver.quit()
    return session_id

# Please note I used parallel execution to scale the test to many devices at a time
# This is not necessary please focus on the retry loop in the test function
if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(test) for _ in range(25)]
        concurrent.futures.wait(futures)
        for index,future in enumerate(futures):
            print(f'{index}: {future.result()}')

