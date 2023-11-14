from flask import Flask, render_template, request, redirect
from selenium import webdriver
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.keys import Keys
import time
import uuid
from flask_caching import Cache
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

app = Flask(__name__)
cache = Cache()
cache.init_app(app, config={"CACHE_TYPE": "simple"})

scrapModelDic = {}

def setScrapModel(key, model, timeout):
    scrapModelDic[key] = model

def getScrapModel(key):
    return scrapModelDic.get(key)

class ScrapModel:
    def __init__(self, template_id, scrap_code, scrap_params_html):
        self.TemplateId = template_id
        self.ScrapCode = scrap_code
        self.ScrapParamsHtml = scrap_params_html

chrome_driver_path = 'C:/Users/agrigoryants/Downloads/chromedriver-win64/chromedriver.exe'

class ScrapModel:
    def __init__(self, template_id, scrap_code, scrap_params_html):
        self.TemplateId = template_id
        self.ScrapCode = scrap_code
        self.ScrapParamsHtml = scrap_params_html


def google_search(query, num_results=5):
    
    service = Service(executable_path=chrome_driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get('https://www.google.com/')

        search_input = driver.find_element('name', 'q')

        search_input.send_keys('test')

        search_input.send_keys(Keys.RETURN)

        driver.implicitly_wait(5)



        all_links = driver.find_elements(By.TAG_NAME, 'h3')



        res_json = []

        for link in all_links:

            text = link.text.strip()

            if text:  # Ignore empty text

                res_json.append({"Title":  f'{text}'})

        print(res_json)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser window
        driver.quit()

# if __name__ == "__main__":
#     search_query = "your query here"
#     google_search(search_query, num_results=5)

@app.route('/admin')
def admin():
    # Retrieve all Scrap Models from the memory cache
    scrap_models = scrapModelDic.values()
    return render_template('admin.html', scrap_models=scrap_models)



@app.route('/create_or_edit_scrap_model', methods=['GET', 'POST'])
def create_or_edit_scrap_model():

  template_id = request.form.get('scrap_template_id')
  scrap_model_instance = getScrapModel(template_id) if template_id else None

  if request.method == 'POST':
    scrap_code = request.form.get('scrap_code')
    scrap_params_html = request.form.get('scrap_params_html')

    if scrap_model_instance:
      scrap_model_instance.ScrapCode = scrap_code
      scrap_model_instance.ScrapParamsHtml = scrap_params_html
      setScrapModel(template_id, scrap_model_instance, timeout=2 * 60 * 60)

    else:
      scrap_model_instance = ScrapModel(
        template_id=template_id,
        scrap_code=scrap_code,
        scrap_params_html=scrap_params_html
      )
      setScrapModel(scrap_model_instance.TemplateId, scrap_model_instance, timeout=2 * 60 * 60)

    return redirect('/admin')

  return render_template('upsert_scrap.html', scrap_model=scrap_model_instance)

@app.route('/scrap', methods=['GET', 'POST'])
def scrap():
    templateId = request.args.get('templateId')
    scrap_model = getScrapModel(templateId)
    if request.method == 'POST':
        # Using the 'with' statement to create a context for the WebDriver
        service = Service(executable_path=chrome_driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        

        with webdriver.Chrome(service=service, options=options) as driver:
            return render_template('scrap_result.html', scrap_results = scrap_inner(templateId, request, driver))
    
    return render_template('scrap.html', scrap_model_instance = scrap_model)


def scrap_inner(templateId, request, driver):
    locals = { 'request': request, 'driver': driver, 'res_json': None }
    try:
        scrap_model_instance = getScrapModel(templateId)
        print(scrap_model_instance.ScrapCode)
        exec(scrap_model_instance.ScrapCode, globals(), locals)
        
        return locals['res_json']

    except Exception as e:
        print(f"An error occurred: {e}")
        return [{'Error': f"An error occurred: {e}"}]

if __name__ == '__main__':
    app.run()
