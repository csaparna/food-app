import streamlit as st
from openai import OpenAI
import os
from PIL import Image
import numpy as np
import base64
import datetime
import json

# Function to Display Image
def load_image(img_Bio):
    im = Image.open(img_Bio)
    image = np.array(im)
    return image

# Function to encode the image for openai
def encode_image(img_Bio):
    return base64.b64encode(img_Bio.getvalue()).decode('utf-8')

#function to confirm json else not load
def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

EXAMPLE_LOG = json.dumps(json.loads(
        """
            {
                    "description": "Thai curry with rice",
                    "ingredients": ["cashew nuts", "rice", "beef", "green beans", "curry sauce", "carrots", "green onions"], 
                    "nutrition": {"thai curry":
                            [
                            {"Quantity (cup)":1},
                            {"Calories (kcal)":500},
                            {"Protein (g)": 20},
                            {"Carbohydrates (g)": 45},
                            {"Fat (g)": 15},
                            {"Fiber (g)": 5},
                            {"Sugar (g)": 10},
                            {"Sodium (mg)": 700}
                            ],
                            "bread":
                            [
                            {"Quantity (slice)":2},
                            {"Calories (kcal)":300},
                            {"Protein (g)": 5},
                            {"Carbohydrates (g)":50},
                            {"Fat (g)": 1},
                            {"Fiber (g)": 2},
                            {"Sugar (g)": 5},
                            {"Sodium (mg)": 20}
                            ]
                    }
            }
        """
    )
)
  
internal_prompt_header = """Analyze the image of the food provided by user. Estimate its ingredients, and nutritional information. Below is the JSON format you should use to organize 
        the estimated data. Note that it's filled with dummy data and you should replace fields with the correct information. Respond only in json format."""
user_prompt = "Analyze the image of the food provided by user and respond with encouragement for logging food, a one line name or description of the food, and its total calories and macronutrients"
st.title("Food logger")

my_openai_key = os.environ.get('OPENAI_TEST_KEY')
client = OpenAI(api_key= my_openai_key)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# else:
#     # Display chat messages from history on app rerun
#     for message in st.session_state.messages:
#         if message["role"] == "assistant":
#         #with st.chat_message(message["role"]):
#             st.sidebar.markdown(message["content"])

# Get user input
with st.chat_message("user"):
        img_in_bytesIO = st.file_uploader("Upload a photo to log your meal")
# if query := st.chat_input("Type your question here."):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(query)

if img_in_bytesIO is not None:
    img = load_image(img_in_bytesIO)
    base64_image = encode_image(img_in_bytesIO)

# Add user image to chat history
    st.image(image = img, width =250)
    # st.session_state.messages.append({"role": "assistant", "content": f"{datetime.datetime.now()}\n"})
    # st.session_state.messages.append({"role": "user", "content": st.image(image = img, width =250)})

    #Upload image file to openai
    # file = client.files.create(file=img_file,
    #                             purpose="vision")


    # with st.chat_message("assistant"):
    stream = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[ 
            {"role": "system", 
                "content": [{ "type":"text",
                            "text": user_prompt}]
            },
            {"role": "user",
            "content": [
                {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }]
            }
        ],
        stream=True,
    )
    #response = st.write_stream(stream) 
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        #st.markdown(stream)
        st.write_stream(stream) 
    # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": f"{datetime.datetime.now()}'\n' {response}"})

    response = client.chat.completions.create(
    model=st.session_state["openai_model"],
    messages=[ 
        {"role": "system", 
            "content": [{ "type":"text",
                        "text": f"{internal_prompt_header}\n{EXAMPLE_LOG}"}]
        },
        {"role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }]
        }
    ],
    stream=False,
    )
  
    with st.sidebar:

        st.write(f"{datetime.datetime.now()}\n")
        st.image(image = img, width =100)
        record = response.choices[0].message.content
        if is_json(record):
            st.json(record)
        else:   
            st.write(record)