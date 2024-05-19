import os
import base64
import urllib
import requests
import logging
from PyPDF2 import PdfReader
from openai import OpenAI

# 百度云文本识别配置
OCR_API_KEY = ""
OCR_SECRET_KEY = ""
# API URL
API_URL = ""  # 'https://api.openai-proxy.org/v1'
# API 密钥
API_KEY = ""
# API 模型
API_MODEL = ""  # "gpt-3.5-turbo"
# 要处理的 PDF 路径和输出的 Markdown 路径
PDF_PATH = r"E:\Test\a.pdf"
OUTPUT_DIRECTORY = r"E:\Test\\"

# 日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    try:
        base_filename = get_base_filename(PDF_PATH)
        pdf_file_base64 = get_file_content_as_base64(PDF_PATH, True)
        num_pages = get_pdf_page_count(PDF_PATH)
        ocr_results = perform_ocr(pdf_file_base64, num_pages)
        questions, answers = process_and_answer_questions(ocr_results)

        save_to_file(questions, f"{OUTPUT_DIRECTORY}{base_filename}_OCR试题.md")
        save_to_file(answers, f"{OUTPUT_DIRECTORY}{base_filename}_OCR试题答案.md")
        logging.info("任务完成")
    except Exception as e:
        logging.error(f"An error occurred: {e}")


def get_base_filename(pdf_path):
    return os.path.splitext(os.path.basename(pdf_path))[0]


def get_file_content_as_base64(path, urlencoded=False):
    try:
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            return urllib.parse.quote_plus(content) if urlencoded else content
    except IOError as e:
        logging.error(f"Error reading file: {e}")
        raise


def get_pdf_page_count(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except IOError as e:
        logging.error(f"Error reading PDF file: {e}")
        raise


def perform_ocr(pdf_file_base64, num_pages):
    ocr_results = []
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general?access_token={get_access_token()}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}

    for page in range(1, num_pages + 1):
        payload = f'pdf_file={pdf_file_base64}&pdf_file_num={page}&detect_direction=false&detect_language=false' \
                  f'&vertexes_location=false&paragraph=false&probability=false '
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            ocr_results.append(response.json())
        else:
            logging.error(f"Error in OCR request: {response.text}")
    return ocr_results


def get_access_token():
    try:
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": OCR_API_KEY, "client_secret": OCR_SECRET_KEY}
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return str(response.json().get("access_token"))
        else:
            logging.error(f"Error getting access token: {response.text}")
            raise Exception("Failed to retrieve access token")
    except requests.RequestException as e:
        logging.error(f"Error in access token request: {e}")
        raise


def process_and_answer_questions(ocr_results):
    client = OpenAI(base_url=API_URL, api_key=API_KEY)

    questions_prompt = build_ocr_prompt(ocr_results)
    questions = generate_markdown_content(client, questions_prompt)

    answers_prompt = build_answer_prompt(questions)
    answers = generate_markdown_content(client, answers_prompt)

    return questions, answers


def build_ocr_prompt(ocr_results):
    prompt = ("请根据以下OCR结果整理并重组这份试卷的内容。使用简洁明了的Markdown格式进行排版，但不需要加入Markdown的代码块标记。"
              "保持内容和结构与原试卷一致，去除所有版权相关描述。注意检查并纠正明显的OCR识别错误。")
    for result in ocr_results:
        prompt += "\n\n" + "\n".join([word["words"] for word in result["words_result"]])
    return prompt


def build_answer_prompt(questions):
    return ("你现在扮演一个计算机专业的学生，负责完成以下试题。请直接使用Markdown格式作答，但无需添加Markdown的代码块标记。"
            "确保你的回答是准确、严谨和专业的。"
            "题目如下：\n" + questions)


def generate_markdown_content(client, prompt):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=API_MODEL,
    )
    return chat_completion.choices[0].message.content


def save_to_file(content, file_path):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
    except IOError as e:
        logging.error(f"Error writing to file: {e}")
        raise


if __name__ == '__main__':
    main()
