#!/usr/bin/env python3

import argparse
ap = argparse.ArgumentParser("UDISE district and block scrapper")
ap.add_argument("-s", "--start_from", type=int, help="start from", required=False, default=0)
ap.add_argument("-m", "--max", type=int, help="maximum rows to process", required=False, default=-1)
ap.add_argument("-i", "--input", type=str, help="input filename", required=False, default="11DIstrict and Block updated - UDISE.xlsx")
ap.add_argument("-a", "--attempts", type=int, help="max number of attempts when processing a row fails", required=False, default=5)
ap.add_argument("-w", "--wait", type=int, help="max number of seconds to wait for tables contents to appear after submitting the form", required=False, default=3)
args = ap.parse_args()


# setting up and fine-tuning the program
MAX_ROWS_TO_PROCESS = args.max # -1 to make it unlimited (i.e. to process all rows)
START_FROM = args.start_from
MAX_ATTEMPTS_PER_ROW = args.attempts
SECONDS_TO_WAIT_FOR_TABLE_CONTENTS = args.wait
INPUT_FILENAME = args.input
OUTPUT_FILENAME = f"district_block_output_{START_FROM}-{START_FROM+MAX_ROWS_TO_PROCESS}.xlsx"
SAVE_INTERMEDIATE_FILES = False
ADD_PADDING = True


import os, subprocess, sys
venv_path = os.path.expanduser(f"{os.curdir}/venv_v1")
activate_script = os.path.join(venv_path, "bin", "activate")

SKIP_AUTO_VENV = False # Set to True for not spawning a new process and when already running in venv. This is useful for debugging
if not SKIP_AUTO_VENV and os.getenv("VIRTUAL_ENV") != venv_path:
  if os.path.exists(activate_script):
    command = f"source {activate_script} && VIRTUAL_ENV={venv_path} python " + " ".join(sys.argv)
    subprocess.call(command, shell=True, executable='/bin/bash')
    sys.exit(0)
  else:
    print(f"Error: Virtual environment not found at {venv_path}")
    sys.exit(1)


from PIL import Image
import pandas as pd
import os, pytesseract, io, base64, traceback, signal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def get_captcha_text(udise_code):
  try:
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
    
    if SAVE_INTERMEDIATE_FILES:
      # Save the extracted text to a file
      with open(png_img_path + ".txt", "wt") as file:
        file.write(text)
    
    return text
  except:
    traceback.print_exc()
    return ""


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

  try:
    # Enter text into the search input field
    search_input = driver.find_element(By.XPATH, search_input_xpath)
    search_input.send_keys(udise_code)

    # Enter text into the CAPTCHA input field (for demonstration, use "1234"; replace with actual CAPTCHA value)
    captcha_input = driver.find_element(By.XPATH, captcha_input_xpath)
    captcha_input.send_keys(captcha_text)

    # Submit the form by clicking the submit button
    submit_button = driver.find_element(By.XPATH, submit_button_xpath)
    submit_button.click()

    WebDriverWait(driver, SECONDS_TO_WAIT_FOR_TABLE_CONTENTS).until(EC.presence_of_element_located((By.XPATH, table_contents_xpath)))
    district = get_text(district_xpath)
    block = get_text(block_xpath)
    return district, block
  except Exception:
    return None, None


def save_results():
  df_output = pd.DataFrame(results)
  df_output.to_excel(OUTPUT_FILENAME, index=False)


def signal_handler(signum, frame):
  save_results()
  if 'driver' in globals():
    driver.quit()
  exit(1)


def main():
  if os.path.exists(OUTPUT_FILENAME):
    print(f"Output file {OUTPUT_FILENAME} already exists. Please delete or rename it.")
    exit(1)

  if not os.path.exists("captcha"):
    os.makedirs("captcha")

  df_input = pd.read_excel(INPUT_FILENAME)
  home_url = "https://src.udiseplus.gov.in/home"

  for idx, (_, row) in enumerate(df_input.iterrows(), start=1):
    if idx<START_FROM:
      continue
    if MAX_ROWS_TO_PROCESS != -1 and (idx-START_FROM)>MAX_ROWS_TO_PROCESS:
      break
    if idx%50==0:
      save_results()
    udise_code = row['UDISE Code']
    for attempt in range(1, MAX_ATTEMPTS_PER_ROW+1):
      driver.get(home_url)
      if attempt==1:
        print(f'{idx:,} of {len(df_input):,}', end='')
      else:
        print('.', end='')
      captcha_text = get_captcha_text(udise_code)
      if captcha_text=="":
        continue
      district, block = submit_form(udise_code, captcha_text)
      if not (district==None and block==None):
        results.append({"UDISE Code": udise_code, "District": district, "Block": block})
        break
      elif attempt==MAX_ATTEMPTS_PER_ROW:
        results.append({"UDISE Code": udise_code, "District": district, "Block": block})
    print('')

  save_results()


if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  try:
    results = []
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    main()
  except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
  finally:
    save_results()
    driver.quit()
