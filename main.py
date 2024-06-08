#!/usr/bin/env python3

# setting up and fine-tuning the program
INPUT_FILENAME = "11DIstrict and Block updated - UDISE.xlsx"
OUTPUT_FILENAME = "district_block_output.xlsx"
SAVE_INTERMEDIATE_FILES = False
ADD_PADDING = True
MAX_ROWS = 10 # -1 to make it unlimited (i.e. to process all rows)
MAX_ATTEMPTS_PER_ROW = 2


from PIL import Image
import pandas as pd
import requests, os, pytesseract, time, io, base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def get_captcha_text(udise_code):
  captcha_img_xpath = "//img[@id='captchaId']"
  png_img_path = f"captcha/{udise_code}.png"
  
  # Wait for the CAPTCHA image to be present
  captcha_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, captcha_img_xpath)))
  
  # Get the CAPTCHA image source in base64
  captcha_base64 = driver.execute_script("""
    var img = arguments[0];
    var canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    var ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, img.width, img.height);
    return canvas.toDataURL('image/png').substring(22);
  """, captcha_element)
  
  # Decode the base64 string and save it as an image
  img_data = base64.b64decode(captcha_base64)
  img = Image.open(io.BytesIO(img_data))
  
  if ADD_PADDING:
    # Add padding to the image to ensure OCR works
    width, height = img.size
    padding = 10
    new_width = width + 2 * padding
    new_height = height + 2 * padding
    new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    new_img.paste(img, (padding, padding))
    img = new_img
  
  # Save the image if required
  if SAVE_INTERMEDIATE_FILES:
    img.save(png_img_path)
  
  # Use pytesseract to extract text
  text = pytesseract.image_to_string(img)
  if text == "":
    raise ValueError(f"No text could be detected for {udise_code}")
  
  if SAVE_INTERMEDIATE_FILES:
    # Save the extracted text to a file
    with open(png_img_path + ".txt", "wt") as file:
      file.write(text)
  
  return text


def get_text(xpath):
  script = f"""
      var xpath = "{xpath}";
      var result = document.evaluate(xpath, document, null, XPathResult.STRING_TYPE, null);
      return result.stringValue;
  """
  text = driver.execute_script(script)
  text = text.strip()
  if ":" in text:
    text = text.split(":")[1].strip()
  return text


def submit_form(udise_code, captcha_text):
  search_input_xpath = "//input[@id='search']"
  captcha_input_xpath = "//input[@name='captcha']"
  submit_button_xpath = "//button[@type='submit']"  #"//button[@id='homeSearchBtn']"
  table_contents_xpath = "//table[@id='example']/tbody/tr[1]/td[4]"
  district_xpath = "//table[@id='example']/tbody/tr[1]/td[4]/text()[3]"
  block_xpath = "//table[@id='example']/tbody/tr[1]/td[4]/text()[5]"

  # Enter text into the search input field
  search_input = driver.find_element(By.XPATH, search_input_xpath)
  search_input.send_keys(udise_code)

  # Enter text into the CAPTCHA input field (for demonstration, use "1234"; replace with actual CAPTCHA value)
  captcha_input = driver.find_element(By.XPATH, captcha_input_xpath)
  captcha_input.send_keys(captcha_text)

  # Submit the form by clicking the submit button
  submit_button = driver.find_element(By.XPATH, submit_button_xpath)
  submit_button.click()

  try:
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, table_contents_xpath)))
    district = get_text(district_xpath)
    block = get_text(block_xpath)
    return district, block
  except Exception as e:
    print(f"Error processing UDISE Code {udise_code}: {e}")
    return None, None


if __name__ == "__main__":
  if not os.path.exists("captcha"):
    os.makedirs("captcha")

  df_input = pd.read_excel(INPUT_FILENAME)
  results = []

  for idx, (index, row) in enumerate(df_input.iterrows(), start=1):
    if MAX_ROWS != -1 and idx>MAX_ROWS:
      break
    for _ in range(MAX_ATTEMPTS_PER_ROW):
      print(f'{idx} of {len(df_input)}')
      udise_code = row['UDISE Code']
      home_url = "https://src.udiseplus.gov.in/home"
      driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
      driver.get(home_url)
      captcha_text = get_captcha_text(udise_code)
      district, block = submit_form(udise_code, captcha_text)
      driver.quit()
      if not (district==None and block==None):
        results.append({"UDISE Code": udise_code, "District": district, "Block": block})
        break

  df_output = pd.DataFrame(results)
  df_output.to_excel(OUTPUT_FILENAME, index=False)
