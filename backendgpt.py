
import requests
import time
import json
import re

url = "https://api.together.xyz/v1/chat/completions"
headers = {
    "Authorization": "Bearer 0a12e0c577c401ea0e5d79f44fba4fe49b8ef5b865e864c6f6e6965bb756540d"
}
system_prompt = {
    "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "messages": [
        {"role": "system", "content": "You are an educational tutor that helps students explore topics."},
        {"role": "user", "content": "Why is the sky blue?"}
    ],
    "temperature": 0.7,
    "max_tokens": 300
}









# TOGETHER.AI API SETUP
url = "https://api.together.xyz/v1/chat/completions"
headers = {
    "Authorization": "Bearer 0a12e0c577c401ea0e5d79f44fba4fe49b8ef5b865e864c6f6e6965bb756540d"
}

# YOUR QUESTION TO ANALYZE
user_question = "who invented the chair"



def generate_subtopics(user_question, retries = 3, delay = 2):
    system_prompt = f"""
    You are a learning design assistant.
    
    Given a student's curiosity-based question, your job is NOT to answer it directly. Instead, analyze it and return the following in JSON format:
    
    - subject_area: Which academic subject(s) this question touches (e.g., Science, Math, History, etc.)
    - depth_level: Introductory / Intermediate / Advanced
    - question_type: Factual / Conceptual / Procedural / Opinion / Open-Ended
    - curiosity_tree: A list of 3–5 short, focused subtopics that help explore this question further
    
    Return your result as a raw JSON object **without any code block formatting**, like this:
    {{
      "subject_area": "...",
      "depth_level": "...",
      "question_type": "...",
      "curiosity_tree": [
        "...",
        "...",
        "...",
        "..."
      ]
    }}
    
    Here is the question to analyze:
    "{user_question}"
    """
    
    # REQUEST PAYLOAD
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    # # API CALL
    # response = requests.post(url, headers=headers, json=payload)
    
    # # HANDLE RESPONSE
    # if response.status_code == 200:
    #     print(response.json()["choices"][0]["message"]["content"])
    # else:
    #     print(f"❌ Error {response.status_code}:")
    #     print(response.text)

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]
            if content:
                return json.loads(content)
            else:
                print(f"⚠️ Empty content received on attempt {attempt}")

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print(f"🚫 Too many requests — attempt {attempt}")
            else:
                print(f"❌ HTTP error on attempt {attempt}: {e}")
        
            
        wait_time = delay * (2 ** (attempt - 1)) + (0.5 * attempt)
        print(f"🔁 Retrying in {wait_time:.1f} seconds...\n")
        time.sleep(wait_time)

    print("❌ Max retries reached. Could not generate subtopics.")
    return None







def generate_explanation_and_activity(subtopic, user_question, retries=3, delay=2):
    system_prompt = f"""
    You are an educational tutor and interaction designer that provides clear, engaging explanations for specific topics related to a student's curiosity.

    The student's broader curiosity question is:
    "{user_question}"

    One of the subtopics to help explain this question is:
    "{subtopic}"

    Your task:

    1. Write a explanation about the **subtopic only**. The explanation should:
    - Have a maximum of 500 words and a minimum of 100 words
    - Be written for an undergraduate-level audience
    - Use analogies or simple examples if helpful
    - Avoid heavy technical jargon
    - Do **not** attempt to answer the full original curiosity question

    2. Based on your explanation, choose any random template from the following list:

    Available templates:
    - drag_drop: Drag items into the relevant categories
    - match_pairs: Match terms to their correct definitions
    - fill_blanks: Fill in missing parts of a formula or sentence
    - toggle_true_false: Quickfire true/false quiz

    3. Return your result as a raw JSON object **without any code block formatting**, like this:

    {{
      "Topic": "...",
      "Explanation": "...",
      "Interactive Template": "..."
    }}

    Now, perform the task and return only the JSON object.
    """

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": subtopic}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if content:
                return json.loads(content)
            else:
                print(f"⚠️ Empty response on attempt {attempt}")
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"❌ Attempt {attempt} failed: {e}")
        if attempt < retries:
            print(f"🔁 Retrying in {delay} seconds...\n")
            time.sleep(delay)
        else:
            print("❌ Max retries reached. Could not get explanation and template.")
            return None


# In[249]:


# explanation_json = generate_explanation_and_activity(subtopic, user_question, retries=3, delay=2)


# In[251]:


# print(explanation_json)


# In[252]:


# type(explanation_json)


# In[255]:


def generate_interactive_activity(topic, explanation, template_type = 'drag_drop', retries=3, delay=2):
    system_prompt = f"""
    You are an educational interaction designer.
    
    Given a topic, an explanation, and a selected template type, your job is to generate an interactive activity in the following JSON format:
    For each activity, include around 5-7 questions.
    If the template is `drag_drop`, structure it like this:
    
    {{
      id: "unique-id-for-the-activity",
      type: "drag_drop",
      title: "Title of the Game",
      description: "One-line description of the drag-and-drop activity.",
      draggableElements: [
        {{ id: "id1", label: "Draggable Term 1" }},
        {{ id: "id2", label: "Draggable Term 2" }}
      ],
      droppableBlanks: [
        {{
          id: "drop-1",
          label: "Hint or definition where a term should go",
          correctElementId: "id1"
        }}
      ]
    }}

    Any label should be max 5 words.
    
    If the selected template is `match_pairs`, respond with a JSON object in this format:

    {{
      "id": "photosynthesis-basics",
      "type": "match",
      "title": "Key Concepts in Photosynthesis",
      "description": "Match each photosynthesis-related term with its correct definition.",
      "pairs": [
        {{ "prompt": "Chlorophyll", "match": "Green pigment that captures light energy" }},
        {{ "prompt": "Stomata", "match": "Tiny pores on leaves where gas exchange occurs" }},
      ]
    }}
    
    Instructions:
    - Use `prompt` for terms, processes, or concepts.
    - Use `match` for definitions, functions, or descriptions (max 5 words).
    - Do NOT include:
      - Synonyms (e.g., avoid “plant sugar” → “glucose” if “glucose” is already a prompt)
      - Nicknames (e.g., no “sun sugar” → “glucose”)
      - Repeated ideas
    - Keep explanations short, factual, and directly linked to the topic.
    - Each pair should be unique and unambiguous.
    
    If the template is `fill_blanks`, structure it like this:
    
    {{
      id: "unique-id",
      type: "fill_in_blanks",
      title: "Fill in the Blanks",
      description: "Fill in the blanks using the correct terms.",
      text: "... with ___ and ___",
      blanks: {{
        "1": ["Melanin", "Keratin", "Chlorophyll"],
        "2": ["Melanocytes", "Blood cells", "Nerve cells"]
      }},
      answers: {{
        "1": "Melanin",
        "2": "Melanocytes"
      }}
    }}
    
    If the template is `toggle_true_false`, structure it like this:
    
    {{
      id: "unique-id",
      type: "toggle_true_false",
      title: "True or False",
      description: "Decide if the following statements are true or false.",
      statements: [
        {{ "id": "s1", "text": "Melanin protects the skin from UV radiation.", "correctAnswer": true }}
      ]
    }}
    
    Now generate a JSON object using the format for this template:
    Topic: {topic}
    Explanation: {explanation}
    Interactive Template: {template_type}
    
    Respond ONLY with the JSON object.
    """

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": template_type}
        ],
        "temperature": 0.7,
        "max_tokens": 700
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            if content:
                return content
            else:
                print(f"⚠️ Empty response on attempt {attempt}")
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"❌ Attempt {attempt} failed: {e}")
        if attempt < retries:
            print(f"🔁 Retrying in {delay} seconds...\n")
            time.sleep(delay)
        else:
            print("❌ Max retries reached. Could not generate activity.")
            return None


# In[256]:


# activity_json = generate_interactive_activity(explanation_json['Topic'], explanation_json['Explanation'], retries=3, delay=2)


# In[257]:


# print(activity_json)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




