# main.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
from backendgpt import generate_subtopics
from backendgpt import generate_explanation_and_activity 
from backendgpt import generate_interactive_activity
from fastapi.responses import JSONResponse

app = FastAPI()

# Global store to keep user_question
variable_storage = {}

# define request format
class QuestionInput(BaseModel):
    user_question: str

class SubtopicRequest(BaseModel):
    subtopic: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/topics_to_learn")
def explain(input: QuestionInput):
   

    result = generate_subtopics(
        user_question=input.user_question
    )
    if result is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Something went wrong while generating subtopics. Try again later."}
        )
    
    variable_storage["stored_question"] = input.user_question

    return {
        "subject_area": result.get("subject_area"),
        "depth_level": result.get("depth_level"),
        "question_type": result.get("question_type"),
        "curiosity_tree": result.get("curiosity_tree")
    }


@app.post("/explain_topic")
def generate_explanation(input: SubtopicRequest):
  
    user_question = variable_storage.get("stored_question")

    result = generate_explanation_and_activity(
        subtopic=input.subtopic,
        user_question=user_question
    )

    if result is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Something went wrong while generating the explanation and activity."}
        )

    topic = result.get("Topic")
    explanation = result.get("Explanation")
    template_type = result.get("Interactive Template")

    activity_content = generate_interactive_activity(
        topic=topic,
        explanation=explanation,
        template_type="drag_drop"
    )

    if activity_content is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Something went wrong while generating the interactive activity."}
        )

    return {
        "explanation": explanation,
        "activity_content": activity_content
    }
