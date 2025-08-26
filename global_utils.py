import logging.handlers
import sys
sys.path.insert(0, '.')
import logging
import openai
import os
from openai import OpenAI
from google import genai
from google.genai import types
import re
import json
import ast
import time

#### logger ####
def setup_logger(name, log_file_path, level=logging.INFO, verbose=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    max_limit_bytes = 1024 * 1024 * 8
    backup_count = 5
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=max_limit_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    if not verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

log_file_path = os.path.join(os.environ['LOG_DIR'], 'global_utils.log')
logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)

#### Utilities ####
def read_json(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        return json.load(f)

def save_json(save_json, file_path):
    with open(file_path, 'w', encoding='UTF-8') as f:
        json.dump(save_json, f, indent=2, ensure_ascii=False)

def read_jsonl(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        return [json.loads(line) for line in f]
    
def is_json(response):
    try:
        data = json.loads(response)
        return True
    except:
        return False
    
def save_txt(txt, file_path):
    with open(file_path, 'w', encoding='UTF-8') as f:
        f.write(txt)

#### LLM calls ####
def preprocess_llm_response(response):
    pattern_json = r'```json\s*(.*?)\s*```'
    match_json = re.search(pattern_json, response, re.DOTALL)
    if match_json:
        json_str = match_json.group(1)
        try:
            return json.loads(json_str)
        except:
            try:
                return ast.literal_eval(json_str)
            except:
                return json_str
        
    pattern_json2 = r'json\n(\[\s*{.*}\s*])'
    match_json2 = re.search(pattern_json2, response, re.DOTALL)
    if match_json2:
        json2_str = match_json2.group(1)
        try:
            return json.loads(json2_str)
        except:
            try:
                return ast.literal_eval(json2_str)
            except:
                return json2_str
        
    preprocess_pattern = r'^```(?:\w+)?\s*\n(.*?)\n```$'
    preprocess_match = re.search(preprocess_pattern, response.strip(), re.DOTALL)
    
    if preprocess_match:
        return preprocess_match.group(1).strip()
    
    try:
        return ast.literal_eval(response.strip())
    except:
        return '\n'.join([l for l in response.splitlines() if "```" not in l]).strip()

def run_gpt(user_prompt, developer_prompt, model='gpt-4o-mini-2024-07-18', temperature=1):
    logger.debug(f"\nmodel: {model}\n===developer_prompt===\n{developer_prompt}\n===user_prompt===\n{user_prompt}")
    
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], timeout=60.0)
    
    wait_time = 2
    completion = None
    while completion is None:
        wait_time = wait_time * 2
        
        try:
            completion = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "developer", "content": developer_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            gpt_response = completion.choices[0].message.content
            logger.debug(f"\n===response===\n{gpt_response}")
            return preprocess_llm_response(gpt_response)
        
        except openai.APITimeoutError as e:
            logger.warning(f"OpenAI API returned an API Error: {e}; waiting for {wait_time} seconds")
            time.sleep(wait_time)
        except openai.APIError as e:
            logger.warning(f"OpenAI API returned an API Error: {e}; waiting for {wait_time} seconds")
            time.sleep(wait_time)
        except openai.APIConnectionError as e:
            logger.warning(f"Failed to connect to OpenAI API: {e}; waiting for {wait_time} seconds")
            time.sleep(wait_time)
            
def run_deepseek(user_prompt, system_prompt, model='deepseek-chat', temperature=1):
    logger.debug(f"\nmodel: {model}\n===system_prompt===\n{system_prompt}\n===user_prompt===\n{user_prompt}")
    
    client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com", timeout=60.0)
    
    wait_time = 2
    completion = None
    while completion is None:
        wait_time = wait_time * 2
        
        try:
            completion = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            deepseek_response = completion.choices[0].message.content
            logger.debug(f"\n===response===\n{deepseek_response}")
            return preprocess_llm_response(deepseek_response)
        
        except Exception as e:
            logger.warning(f"DeepSeek API returned an API Error: {e}; waiting for {wait_time} seconds")
            time.sleep(wait_time)
            
def run_gemini(user_prompt, system_prompt, model="gemini-2.0-flash", temperature=1):
    logger.debug(f"\nmodel: {model}\n===system_prompt===\n{system_prompt}\n===user_prompt===\n{user_prompt}")
    
    client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])
    
    wait_time = 2
    response = None
    while response is None:
        wait_time = wait_time * 2
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    top_p=0.95,
                    frequency_penalty=0.23,
                    presence_penalty=0.23),
                contents=user_prompt,
            )
            
            gemini_response = response.text
            logger.debug(f"\n===response===\n{gemini_response}")
            return preprocess_llm_response(gemini_response)
            
        except Exception as e:
            logger.warning(f"Gemini API returned an API Error: {e}; waiting for {wait_time} seconds")
            time.sleep(wait_time)
            
            
def run_llm(user_prompt, system_prompt='You are a helpful assistant.', model='gpt-4o-mini-2024-07-18', temperature=1.0):
    if 'gpt' in model:
        return run_gpt(user_prompt, system_prompt, model, temperature)
    elif 'deepseek' in model:
        return run_deepseek(user_prompt, system_prompt, model, temperature)
    elif 'gemini' in model:
        return run_gemini(user_prompt, system_prompt, model, temperature)
    else:
        logger.error(f"Invalid model card: {model}")
        raise KeyError