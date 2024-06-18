import json
import re
import logging
import random
from openai import OpenAI
from sqlalchemy.orm import Session
from fastapi import HTTPException  # 추가된 부분
from DB_app.models import Article, Grading, Question
from DB_app.DBsetting import SessionLocal
from app.Prompt import *
from DB_app import crud

from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화 함수
def initialize_openai_client():
    try:
        OPENAI_API_KEY = os.getenv('GPT_API_KEY')
        if not OPENAI_API_KEY:
            raise ValueError("API key is not set")
        print("gpt 키 가져오기 성공:", OPENAI_API_KEY)
    except Exception as e:
        print("gpt 키 가져오기 실패:", e)

    return OpenAI(api_key=OPENAI_API_KEY)

# 전역 클라이언트 초기화
openai_client = initialize_openai_client()

def get_result_from_gpt(client, prompt, user):
    try:
        completion = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user}])
        prompt_json = completion.choices[0].message.content
        logger.debug(f"GPT 응답: {prompt_json}")
        return prompt_json
    except Exception as e:
        logger.error(f"Error getting result from GPT: {e}")
        raise

def change_to_dict(text):
    try:
        if isinstance(text, dict):
            return text
        if text.startswith('```json'):
            text = text[7:-3].strip()
        elif text.startswith('```'):
            text = text[3:-3].strip()
        
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        json_text = cleaned_text[cleaned_text.find('{'):cleaned_text.rfind('}')+1].strip()
        json_text = re.sub(r'\\u[0-9a-fA-F]{4}', '', json_text)
        
        dictionary = json.loads(json_text)
        return dictionary
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {e}")
        logger.error(f"문제가 된 응답: {text}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

def insert_and_shuffle_options(answer, options):
    options_list = [str(opt) if opt is not None else "" for opt in list(options)]
    options_list.append(str(answer) if answer is not None else "")
    random.shuffle(options_list)
    logger.debug(f"Options list after shuffle: {options_list}")
    return options_list

def seperate(para_dictionary):
    paragraph_values = [value for key, value in para_dictionary.items() if key.startswith('paragraph')]
    sentence_dictionary = {}
    for i, paragraph in enumerate(paragraph_values):
        sentences = paragraph.split('.')
        for j, sentence in enumerate(sentences):
            if sentence.strip():
                key = f"sentence {i+1}-{j+1}"
                sentence_dictionary[key] = sentence.strip()
    return sentence_dictionary

def remove_duplicate_keyword(dictionary):
    unique_values = set(dictionary.values())
    unique_dict = {}
    for key, value in dictionary.items():
        if value in unique_values:
            unique_dict[key] = value
            unique_values.remove(value)
    return unique_dict

def make_keyword_question_para_value(level, keywords_dict):
    options = ["첫번째", "두번째", "세번째", "네번째"]
    para_mapping = {
        '첫번째': 1,
        '두번째': 2,
        '세번째': 3,
        '네번째': 4
    }

    def get_random_para(option_list):
        para = random.choice(option_list)
        rand_para = para_mapping[para]
        return para, rand_para

    if level == 1:
        if keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2']:
            return "전체", 1
        else:
            return get_random_para(options[:2])

    if level == 2:
        if keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2'] == keywords_dict['paragraph keyword 3']:
            return "전체", 1
        elif keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2']:
            return "1문단과 2문단", 1
        elif keywords_dict['paragraph keyword 2'] == keywords_dict['paragraph keyword 3']:
            return "2문단과 3문단", 2
        elif keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 3']:
            return "1문단과 3문단", 1
        else:
            return get_random_para(options[:3])

    if level == 3:
        if keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2'] == keywords_dict['paragraph keyword 3'] == keywords_dict['paragraph keyword 4']:
            return "전체", 1, 0, 0
        elif keywords_dict['paragraph keyword 2'] == keywords_dict['paragraph keyword 3'] == keywords_dict['paragraph keyword 4']:
            return "1문단", 1, "2문단, 3문단, 4문단", 2
        elif keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2'] == keywords_dict['paragraph keyword 3']:
            return "1문단, 2문단, 3문단", 1, "4문단", 4
        elif keywords_dict['paragraph keyword 1'] == keywords_dict['paragraph keyword 2']:
            para, rand_para = "1문단과 2문단", 1
            para2, rand_para2 = get_random_para(options[2:4])
            return para, rand_para, para2, rand_para2
        elif keywords_dict['paragraph keyword 3'] == keywords_dict['paragraph keyword 4']:
            para, rand_para = "3문단과 4문단", 3
            para2, rand_para2 = get_random_para(options[:2])
            return para, rand_para, para2, rand_para2
        else:
            para, para2 = random.sample(options, 2)
            rand_para = para_mapping[para]
            rand_para2 = para_mapping[para2]
            return para, rand_para, para2, rand_para2

def generate_options(answer_key, unique_keyword_sentence_dict):
    options_for_answer = [unique_keyword_sentence_dict[key] for key in unique_keyword_sentence_dict if key != answer_key]
    options_for_answer = [str(opt) if opt is not None else "" for opt in options_for_answer]
    random_options = random.sample(options_for_answer, 3)
    return random_options

def make_keyword_question_para(para, rand_para, unique_keywords_dict, num):
    keyword_result_add = {
        f"keyword_question_{num}": f"글을 읽고 {para} 문단의 핵심단어를 고르시오.",
        f"keyword_answer_{num}": unique_keywords_dict[f'paragraph keyword {rand_para}'] if unique_keywords_dict[f'paragraph keyword {rand_para}'] is not None else "",
        f"keyword_option_{num}": list(set(insert_and_shuffle_options(
            unique_keywords_dict[f'paragraph keyword {rand_para}'] if unique_keywords_dict[f'paragraph keyword {rand_para}'] is not None else "", 
            generate_options(f'paragraph keyword {rand_para}', unique_keywords_dict)))),
    }
    return keyword_result_add

def rand_key_and_sentence(article_sentence, unique_keyword_dict, except_key):
    except_unique_keyword_dict = {k: v for k, v in unique_keyword_dict.items() if k not in except_key}
    if not except_unique_keyword_dict:
        return None, None
    random_key = random.choice(list(except_unique_keyword_dict.keys()))
    matched_value = next((value for key, value in article_sentence.items() if key[-4:] == random_key[-4:]), None)
    return random_key, matched_value

def rand_keys_and_matched_sentences(level, article_sentence, unique_keyword_dict):
    except_key = ['paragraph keyword 1', 'paragraph keyword 2', 'paragraph keyword 3', 'paragraph keyword 4']
    random_keys = []
    matched_sentences = []
    for i in range(0,level+1,1):
        random_key, matched_value = rand_key_and_sentence(article_sentence, unique_keyword_dict, except_key)
        except_key.append(random_key)
        random_keys.append(random_key)
        matched_sentences.append(matched_value)
    return random_keys, matched_sentences

def make_keyword_question_sentence(matched_value, random_key, unique_keywords_dict, num):
    keyword_result_add = {
        f"keyword_question_{num}": f"'{matched_value}' 해당 문장의 핵심 단어를 고르시오.",
        f"keyword_answer_{num}": unique_keywords_dict[f'{random_key}'],
        f"keyword_option_{num}": list(set(insert_and_shuffle_options(unique_keywords_dict[f'{random_key}'], generate_options([f'{random_key}'], unique_keywords_dict)))),
    }
    return keyword_result_add

def generate_voca_question(level, voca_questions_dict):
    targets = ['기사 안의 단어 중 ', '기사 안의 단어 ', 'example)']
    for target in targets:
        for key in list(voca_questions_dict.keys()):
            value = voca_questions_dict[key]
            if target in value:
                voca_questions_dict[key] = value.replace(target, '')
    
    if level == 1 :
        question_num_start, question_num_last, start_key = 1, 4, 0
    elif level == 2 :
        question_num_start, question_num_last, start_key = 1, 5, 0
    elif level == 3 :
        question_num_start, question_num_last, start_key = 1, 4, 18

    voca_result = {}
    keys = list(voca_questions_dict.keys())
    for i in range(question_num_start, question_num_last):
        question_index = (i - question_num_start) * 3 + start_key
        voca_result[f"voca_question_{i}"] = voca_questions_dict[keys[question_index]]
        voca_result[f"voca_answer_{i}"] = voca_questions_dict[keys[question_index + 1]]
        voca_result[f"voca_option_{i}"] = list(set(insert_and_shuffle_options(voca_questions_dict[keys[question_index + 1]], voca_questions_dict[keys[question_index + 2]])))
    if level == 3:
        voca_result_add = {
            "voca_question_4": f"'{voca_questions_dict['word_1']}' 을/를 올바르게 사용한 문장을 고르시오.",
            "voca_answer_4": voca_questions_dict['correct1_1'],
            "voca_option_4": list(set(insert_and_shuffle_options(voca_questions_dict['correct1_1'],[voca_questions_dict['incorrect1_1'],voca_questions_dict['incorrect1_2'],voca_questions_dict['incorrect1_3']]))),

            "voca_question_5": f"'{voca_questions_dict['word_2']}' 을/를 올바르게 사용하지 못한 문장을 고르시오.",
            "voca_answer_5": voca_questions_dict['incorrect2_1'],
            "voca_option_5": list(set(insert_and_shuffle_options(voca_questions_dict['incorrect2_1'], [voca_questions_dict['correct2_1'],voca_questions_dict['correct2_2'],voca_questions_dict['correct2_3']]))),
        }
        voca_result.update(voca_result_add)

    return voca_result

def generate_organize_question(level, organize_questions_dict):
    organize_result = {}
    for i in range(1, level+3):
        organize_result[f"organize_question_{i}"] = organize_questions_dict[f'question{i}']
        organize_result[f"organize_answer_{i}"] = organize_questions_dict[f'answer{i}']
        organize_result[f"organize_option_{i}"] = list(set(insert_and_shuffle_options(organize_questions_dict[f'answer{i}'], organize_questions_dict[f'options{i}'])))
    
    return organize_result

def generate_short(client, sub):
    logger.info("Starting generate_short function")
    short_article_json = get_result_from_gpt(client, generate_article_short, sub)
    logger.debug(f"short_article_json: {short_article_json}")
    
    short_article_dict = change_to_dict(short_article_json)
    logger.debug(f"short_article_dict: {short_article_dict}")
    
    short_article_sentence = seperate(short_article_dict)
    logger.debug(f"short_article_sentence: {short_article_sentence}")
    
    short_keyword_json = get_result_from_gpt(client, keyword_prompt_short, json.dumps(short_article_sentence) + json.dumps(how_to_find_a_keyword))
    logger.debug(f"short_keyword_json: {short_keyword_json}")
    
    short_keyword_dict = change_to_dict(short_keyword_json)
    logger.debug(f"short_keyword_dict: {short_keyword_dict}")
    
    short_unique_keyword_dict = remove_duplicate_keyword(short_keyword_dict)
    logger.debug(f"short_unique_keyword_dict: {short_unique_keyword_dict}")
    
    short_keyword_result = {}
    short_para, short_rand_para = make_keyword_question_para_value(1, short_keyword_dict)
    logger.debug(f"short_para: {short_para}, short_rand_para: {short_rand_para}")
    
    short_keyword_result_add = make_keyword_question_para(short_para, short_rand_para, short_unique_keyword_dict, 1)
    logger.debug(f"short_keyword_result_add: {short_keyword_result_add}")
    
    short_keyword_result.update(short_keyword_result_add)
    
    short_random_keys, short_matched_sentences = rand_keys_and_matched_sentences(1, short_article_sentence, short_unique_keyword_dict)
    logger.debug(f"short_random_keys: {short_random_keys}, short_matched_sentences: {short_matched_sentences}")
    
    for i in range(0, 2):
        short_keyword_result_add = make_keyword_question_sentence(short_matched_sentences[i], short_random_keys[i], short_unique_keyword_dict, num=i+2)
        logger.debug(f"short_keyword_result_add_{i+2}: {short_keyword_result_add}")
        short_keyword_result.update(short_keyword_result_add)
    
    short_voca_json = get_result_from_gpt(client, voca_prompt_short, json.dumps(short_article_dict))
    logger.debug(f"short_voca_json: {short_voca_json}")
    
    short_voca_dict = change_to_dict(short_voca_json)
    logger.debug(f"short_voca_dict: {short_voca_dict}")
    
    short_voca_result = generate_voca_question(1, short_voca_dict)
    logger.debug(f"short_voca_result: {short_voca_result}")
    
    short_organize_json = get_result_from_gpt(client, organize_prompt_short, json.dumps(short_article_dict) + json.dumps(sample_questions_when_creating_literacy_questions))
    logger.debug(f"short_organize_json: {short_organize_json}")
    
    short_organize_dict = change_to_dict(short_organize_json)
    logger.debug(f"short_organize_dict: {short_organize_dict}")
    
    short_organize_result = generate_organize_question(1, short_organize_dict)
    logger.debug(f"short_organize_result: {short_organize_result}")
    
    short_summary_json = get_result_from_gpt(client, summary_prompt_short, json.dumps(short_article_dict))
    logger.debug(f"short_summary_json: {short_summary_json}")
    
    short_summary_dict = change_to_dict(short_summary_json)
    logger.debug(f"short_summary_dict: {short_summary_dict}")

    return short_article_dict, short_keyword_result, short_voca_result, short_organize_result, short_summary_dict

def generate_mid(client, sub):
    mid_article_json = get_result_from_gpt(client, generate_article_mid, sub)
    mid_article_dict = change_to_dict(mid_article_json)
    mid_article_sentence = seperate(mid_article_dict)
    mid_keyword_json = get_result_from_gpt(client, keyword_prompt_mid, json.dumps(mid_article_sentence) + json.dumps(how_to_find_a_keyword))
    mid_keyword_dict = change_to_dict(mid_keyword_json)
    mid_unique_keyword_dict = remove_duplicate_keyword(mid_keyword_dict)
    mid_keyword_result = {}
    mid_para, mid_rand_para = make_keyword_question_para_value(2, mid_keyword_dict)
    mid_keyword_result_add = make_keyword_question_para(mid_para, mid_rand_para, mid_unique_keyword_dict, 1)
    mid_keyword_result.update(mid_keyword_result_add)
    mid_random_keys, mid_matched_sentences = rand_keys_and_matched_sentences(2, mid_article_sentence, mid_unique_keyword_dict)
    for i in range(0,3):
        mid_keyword_result_add = make_keyword_question_sentence(mid_matched_sentences[i], mid_random_keys[i], mid_unique_keyword_dict, num=i+2)
        mid_keyword_result.update(mid_keyword_result_add)
    mid_voca_json = get_result_from_gpt(client, voca_prompt_mid, json.dumps(mid_article_dict))
    mid_voca_dict = change_to_dict(mid_voca_json)
    mid_voca_result = generate_voca_question(2, mid_voca_dict)
    mid_organize_json = get_result_from_gpt(client, organize_prompt_mid, json.dumps(mid_article_dict) + json.dumps(sample_questions_when_creating_literacy_questions))
    mid_organize_dict = change_to_dict(mid_organize_json)
    mid_organize_result = generate_organize_question(2, mid_organize_dict)
    mid_summary_json = get_result_from_gpt(client, summary_prompt_mid, json.dumps(mid_article_dict))
    mid_summary_dict = change_to_dict(mid_summary_json)

    return mid_article_dict, mid_keyword_result, mid_voca_result, mid_organize_result, mid_summary_dict

def generate_long(client, sub):
    long_article_json = get_result_from_gpt(client, generate_article_long, sub)
    long_article_dict = change_to_dict(long_article_json)
    long_article_sentence = seperate(long_article_dict)
    long_keyword_json = get_result_from_gpt(client, keyword_prompt_long, json.dumps(long_article_sentence) + json.dumps(how_to_find_a_keyword))
    long_keyword_dict = change_to_dict(long_keyword_json)
    long_unique_keyword_dict = remove_duplicate_keyword(long_keyword_dict)
    long_keyword_result = {}
    long_para, long_rand_para, long_para2, long_rand_para2 = make_keyword_question_para_value(3, long_keyword_dict)
    long_keyword_result_add = make_keyword_question_para(long_para, long_rand_para, long_unique_keyword_dict, 1)
    long_keyword_result.update(long_keyword_result_add)
    if long_para2 == 0:
        long_random_keys, long_matched_sentences = rand_keys_and_matched_sentences(3, long_article_sentence, long_unique_keyword_dict)
        for i in range(0,4):
            long_keyword_result_add = make_keyword_question_sentence(long_matched_sentences[i], long_random_keys[i], long_unique_keyword_dict, num=i+2)
            long_keyword_result.update(long_keyword_result_add)
    else:
        long_keyword_result_add = make_keyword_question_para(long_para2, long_rand_para2, long_unique_keyword_dict, 2)
        long_keyword_result.update(long_keyword_result_add)
        long_random_keys, long_matched_sentences = rand_keys_and_matched_sentences(3, long_article_sentence, long_unique_keyword_dict)
        for i in range(0,3):
            long_keyword_result_add = make_keyword_question_sentence(long_matched_sentences[i], long_random_keys[i], long_unique_keyword_dict, num=i+3)
            long_keyword_result.update(long_keyword_result_add)
    long_voca_json = get_result_from_gpt(client, voca_prompt_long, json.dumps(long_article_dict))
    long_voca_dict = change_to_dict(long_voca_json)
    long_voca_result = generate_voca_question(3, long_voca_dict)
    long_organize_json = get_result_from_gpt(client, organize_prompt_long, json.dumps(long_article_dict) + json.dumps(sample_questions_when_creating_literacy_questions))
    long_organize_dict = change_to_dict(long_organize_json)
    long_organize_result = generate_organize_question(3, long_organize_dict)
    long_summary_json = get_result_from_gpt(client, summary_prompt_long, json.dumps(long_article_dict))
    long_summary_dict = change_to_dict(long_summary_json)

    return long_article_dict, long_keyword_result, long_voca_result, long_organize_result, long_summary_dict

def create_article_and_questions(client, sub, level):
    logger.info(f"Creating article and questions for level: {level}")
    if level == 'short':
        newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result = generate_short(client, sub)
    elif level == 'middle':
        newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result = generate_mid(client, sub)
    elif level == 'long':
        newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result = generate_long(client, sub)
    else:
        raise ValueError(f"Unknown article length: {level}")

    return newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result

def get_next_article_code(db: Session) -> str:
    last_article = db.query(Article).order_by(Article.article_code.desc()).first()
    if last_article and last_article.article_code and isinstance(last_article.article_code, str):
        try:
            last_code = int(last_article.article_code.split('-')[1])
            new_code = f"{last_code + 1:03d}"
        except (IndexError, ValueError) as e:
            logger.error(f"Error parsing article code: {e}")
            new_code = "001"
    else:
        new_code = "001"
    return f"ART-{new_code}"

def generate_article(client, db, sub, level):
    retry_count = 0
    max_retries = 9
    while retry_count < max_retries:
        try:
            newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result = create_article_and_questions(client, sub, level)
            logger.info(f"newspaper_dict_para: {newspaper_dict_para}")
            logger.info(f"keyword_result: {keyword_result}")
            logger.info(f"voca_result: {voca_result}")
            logger.info(f"organize_result: {organize_result}")
            logger.info(f"summary_result: {summary_result}")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}. {level} 기사, 문제 다시 실행 중...")
            retry_count += 1

    if retry_count == max_retries:
        raise Exception("Maximum retries reached. Failed to generate article and questions.")

    new_article_code = f"{get_next_article_code(db)}-{level}"
    logger.info(f"new_article_code: {new_article_code}")
    newspaper_dict_para["article_code"] = new_article_code
    newspaper_dict_para["Content"] = ""
    return crud.save_generated_data(db, level, newspaper_dict_para, keyword_result, voca_result, organize_result, summary_result, sub)

def generate_short_article(client, db, sub):
    return generate_article(client, db, sub, 'short')

def generate_middle_article(client, db, sub):
    return generate_article(client, db, sub, 'middle')

def generate_long_article(client, db, sub):
    return generate_article(client, db, sub, 'long')

def initialize_generation():
    content_list = ['과학', '사회', '수학', '국어']
    sub = random.choice(content_list)
    return openai_client, sub

def generate_all():
    client, sub = initialize_generation()
    db = SessionLocal()
    response_data = {
        "articles": []
    }
    response_data["articles"].append(generate_short_article(client, db, sub))
    response_data["articles"].append(generate_middle_article(client, db, sub))
    response_data["articles"].append(generate_long_article(client, db, sub))
    db.close()
    return response_data

def get_openai_summary(user_summary, ai_summary):
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": '''당신은 국어교사이다.
                                            두번의 입력이 들어올 것이다.
                                            첫번째 입력을 두번째 입력과 비교하라.
                                            잘한 부분, 못한 부분을 지도하라.
                                            첫번째 입력을 첨삭하는 것이 목적이다.
                                            첨삭내용은 세문장으로 출력하라.
            '''},
            {"role": "user", "content": user_summary},
            {"role": "user", "content": ai_summary}
        ])
    
    result_text = completion.choices[0].message.content
    logger.info("OpenAI result: %s", result_text)

    summary_text = f"학생이 한 요약: {user_summary}\n\n AI가 한 요약: {ai_summary}\n\n총평: {result_text}"
    return summary_text


def summarize_article(article_code: str, db: Session):
    try:
        latest_question_code = db.query(
            Question.question_code
        ).filter(
            Question.article_code == article_code
        ).order_by(
            Question.question_code.desc()
        ).first()

        if not latest_question_code:
            raise HTTPException(status_code=404, detail="No questions found for the given article code")

        ai_summary = db.query(
            Question.answer
        ).filter(
            Question.article_code == article_code,
            Question.question_code == latest_question_code[0]
        ).first()

        user_summary = db.query(
            Grading.submitted_answer
        ).filter(
            Grading.article_code == article_code,
            Grading.question_code == latest_question_code[0]
        ).first()

        return get_openai_summary(
            user_summary=user_summary[0] if user_summary else "None",
            ai_summary=ai_summary[0] if ai_summary else "None"
        )
    except Exception as e:
        logger.error("Error summarizing article: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
