from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# in seconds, max wait?
waitTime = 10

# Ref: http://selenium-python.readthedocs.io/api.html#locate-elements-by

def byId(idStr, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.presence_of_element_located(
            (By.ID, idStr)
        )
    )

def byCss(cssSelector, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, cssSelector)
        )
    )

def byName(name, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.presence_of_element_located(
            (By.NAME, name)
        )
    )

def byClass(className, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, className)
        )
    )

def byCssSelected(cssSelector, driverObj):    
    return WebDriverWait(driverObj, waitTime).until(
        EC.element_located_to_be_selected(
            (By.CSS_SELECTOR, cssSelector)
        )
    )

def byCssVisible(cssSelector, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, cssSelector)
        )     
    )

def byIdVisible(idStr, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.visibility_of_element_located(
            (By.ID, idStr)
        )
    )

def byCssClickable(cssSelector, driverObj):
    return WebDriverWait(driverObj, waitTime).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, cssSelector)
        )     
    )