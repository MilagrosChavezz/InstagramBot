from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import pandas as pd
from datetime import datetime

# Cargar credenciales
load_dotenv()
username = os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INTAGRAM_PASSWORD')

def login_to_instagram():
    print("Iniciando login..")

    if not username or not password:
        raise ValueError("Faltan credenciales")

    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--start-maximized')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.instagram.com/")
    print("Esperando login...")

    username_input = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']"))
    )
    password_input = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
    )

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button = WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    login_button.click()

    time.sleep(10)

    
    try:
        not_now_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]"))
        )
        not_now_button.click()
    except:
        pass

    return driver

def get_followings(driver, username):
    print(f"Obteniendo seguidos de {username}")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    try:
        followings_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/following/')]"))
        )
        driver.execute_script("arguments[0].click();", followings_link)  # Usa JS para evitar bloqueos
        time.sleep(5)
    except Exception as e:
        print(f"Error al abrir la lista de seguidos: {e}")
        return []


    accounts_class = "_ap3a._aaco._aacw._aacx._aad7._aade"
    following_container_xpath = "//div[contains(@class, 'xyi19xy')]"

    try:
        following_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, following_container_xpath))
        )
    except:
        print("No se encontró el contenedor de seguidos")
        return []

    start_time = datetime.now()
    following_list = []

    while (datetime.now() - start_time).total_seconds() < 300:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", following_container)
        time.sleep(2)

        following_elements = driver.find_elements(By.CLASS_NAME, accounts_class)
        following_list = [elem.text for elem in following_elements if elem.text]

    
    return following_list  



def get_followers(driver, username):
    print(f"Obteniendo seguidores de {username}")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    try:
        followers_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]"))
        )
        driver.execute_script("arguments[0].click();", followers_link)  
        time.sleep(5)
    except Exception as e:
        print(f"Error al abrir la lista de seguidores: {e}")
        return []

    
    accounts_class = "_ap3a._aaco._aacw._aacx._aad7._aade"
    followers_container_xpath = "//div[contains(@class, 'xyi19xy')]"

    try:
        followers_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, followers_container_xpath))
        )
    except:
        print("No se encontró el contenedor de seguidores")
        return []

    start_time = datetime.now()
    followers_list = []

    while (datetime.now() - start_time).total_seconds() <  300:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", followers_container)
        time.sleep(2)

        followers_elements = driver.find_elements(By.CLASS_NAME, accounts_class)
        followers_list = [elem.text for elem in followers_elements if elem.text]

        

    return followers_list

def save_to_excel(data_list, column_name, followers=None):
    df = pd.DataFrame(data_list, columns=[column_name])

    if column_name == "following" and followers is not None:
        df['Follower'] = df[column_name].apply(lambda x: 'Yes' if x in followers else 'No')

    filename = f'{column_name}.xlsx'
    df.to_excel(filename, index=False)
    return filename

if __name__ == "__main__":
    driver = login_to_instagram()
    
    followers = get_followers(driver, username)
    excel_followers = save_to_excel(followers, "followers")
    
    following = get_followings(driver, username)
    excel_following = save_to_excel(following, "following", followers)

    print(f"Archivos guardados: {excel_followers}, {excel_following}")

    input("Presiona Enter para cerrar")
    driver.quit()
