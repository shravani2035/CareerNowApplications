import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

df = pd.read_csv(config["csv_path"])
jobs = df.to_dict(orient="records")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def safe_type(element, text):
    try:
        element.clear()
    except:
        pass
    element.send_keys(text)

def auto_upload(file_keywords, file_path):
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        for inp in inputs:
            if any(kw in inp.get_attribute("name").lower() for kw in file_keywords) or \
               any(kw in inp.get_attribute("id").lower() for kw in file_keywords):
                inp.send_keys(file_path)
                return True
    except:
        pass

    try:
        for kw in file_keywords:
            elems = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{kw}')]")
            for e in elems:
                try:
                    e.click()
                    time.sleep(1)
                    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                    for inp in file_inputs:
                        inp.send_keys(file_path)
                        return True
                except:
                    continue
    except:
        pass
    return False

for job in jobs:
    link = job.get("Link")
    if not link or not str(link).startswith("http"):
        continue

    print(f"\nOpening job: {job.get('Name', '')} — {link}")
    driver.get(link)
    time.sleep(5)

    field_map = {
        "name": config["full_name"],
        "full name": config["full_name"],
        "email": config["email"],
        "phone": config["phone"],
        "linkedin": config["linkedin"]
    }

    inputs = driver.find_elements(By.TAG_NAME, "input")
    for inp in inputs:
        try:
            name_attr = inp.get_attribute("name") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            label_text = ""
            try:
                label_text = driver.find_element(By.XPATH, f"//label[@for='{inp.get_attribute('id')}']").text
            except:
                pass

            combined = f"{name_attr} {placeholder} {label_text}".lower()
            for key, val in field_map.items():
                if key in combined:
                    safe_type(inp, val)
                    break
        except:
            continue

    print("Uploading resume...")
    auto_upload(["resume", "cv"], os.path.abspath(config["resume_path"]))
    time.sleep(2)

    print("Uploading cover letter...")
    auto_upload(["cover", "letter"], os.path.abspath(config["cover_letter_path"]))
    time.sleep(2)

    print("Please review this application manually in the browser, then submit or close it.")
    input("Press Enter here to continue to the next application...")