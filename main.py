import streamlit as st
import requests
from api import create_chat_completion, _get_headers
from dotenv import load_dotenv
import os
import session
from typing import Dict, List, Tuple
from dialogues import default_convo
import io

load_dotenv()

name_2_usecase_name: Dict = {
    "Sales Manager": "sales_manager_persona",
    "Compliance Officer": "compliance_officer_persona",
    "Product Manager": "product_manager_persona",
    }

# create sessions for experts
def create_session_experts(expert: str, user_input: str) -> str:
    payload = {'params': {}, 'files': {'Transcript': ('transcript.txt', io.BytesIO(user_input.encode('utf-8')))}, 'json': {}}
    res = requests.post(f"http://localhost:8111/api/v1/usecases/{expert}/session", **payload, headers=_get_headers())
    return str(res.content.decode())

# create sessions for 1_rm_client usecase
def create_session_useacse(user_input: str, expert_input: str) -> str:
    payload = {'params': {'Bank_Policies': 'policy_1.txt', 'Courses': 'wealth_management_courses'}, 'files': {'Transcript': ('transcript.txt', io.BytesIO(user_input.encode('utf-8'))), 'expert_data': ('test_transcript.txt', io.BytesIO(expert_input.encode('utf-8')))}, 'json': {}}
    res = requests.post(f"http://localhost:8111/api/v1/usecases/1_RM_Client/session", **payload, headers=_get_headers())
    return str(res.content.decode())


def main():
    st.set_page_config(page_title="Compliance Demo v2", layout='wide')

    st.header("RM Client Demo v2")

    col1, col2 = st.columns(2)
    # Text input for user queries
    experts = []
    with col1:
        experts = ["Sales Manager", "Compliance Officer", "Product Manager"]
        experts_selected = st.multiselect("Select Experts", experts, default=experts)
    with col2:
        user_input = st.text_area("Enter the conversation:", value=default_convo, height=400)

    if st.button("Start Conversation"):

        res_list: List[Tuple] = []

        for expert in experts_selected:
            expert_usecase: str = name_2_usecase_name[expert]
            
            session_id = create_session_experts(expert_usecase, user_input)
            print(f"{expert}'s session ID: {session_id}")
            chat_payload = {'model': expert_usecase, 'messages': [{'role': 'system', 'content': ''}], 'max_tokens': 700}
            res = create_chat_completion(chat_payload=chat_payload, session_id=session_id)
            
            # extract content
            content: str = dict(res.json())["choices"][0]["message"]["content"]
            content = content.replace("#", "")
            
            res_list.append((expert, content))


        if not len(res_list) == len(experts_selected):
            st.error("Oops some experts didn't work~")
            st.stop()

        # display the results
        expert_data: str = "" 
        with st.expander("Expert Feedbacks", expanded=True):
            for i, message in enumerate(res_list):
                with st.chat_message(message[0], avatar="🧑💎🕍🚐🍟🏫🚠"[i]):
                    st.write(message[1])

                    expert_data += f"Expert: {message[0]}\n\nOpinion: {message[1]}*********\n\n"

        # create session for the rm usecase
        usecase_session_id = create_session_useacse(user_input, expert_data)
        print(f"1_RM_Client demo session ID: {usecase_session_id}")

        chat_payload = {'model': "1_RM_Client", 'messages': [{'role': 'system', 'content': ''}], 'max_tokens': None}
        res = create_chat_completion(chat_payload, usecase_session_id)
        # extract content
        content: str = dict(res.json())["choices"][0]["message"]["content"]
        
        with st.expander("Analysis Report", expanded=True):
            with st.chat_message("Assistant"):
                st.write(content)

        

if __name__ == "__main__":
    main()