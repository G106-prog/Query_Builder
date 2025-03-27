import gradio as gr
import pandas as pd
import sqlite3
import openai
import os

# Set OpenAI API Key (Replace with your actual API key or use environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_table_from_csv(file):
    if file is None:
        return "No file uploaded yet."
    
    df = pd.read_csv(file.name)
    conn = sqlite3.connect(':memory:')  # Use in-memory database
    df.to_sql('uploaded_data', conn, if_exists='replace', index=False)
    conn.commit()
    return "Table 'uploaded_data' created successfully!"

def show_schema(file):
    if file is None:
        return "No file uploaded yet."
    
    df = pd.read_csv(file.name)
    columns = "\n".join(df.columns)  # Show column names one by one
    return f"Table Name: uploaded_data\nColumns:\n{columns}"

def generate_sql_query(file, nlp_question):
    if file is None:
        return "No file uploaded yet."
    
    df = pd.read_csv(file.name)
    column_names = ", ".join(df.columns)
    
    prompt = (f"Convert this natural language question into an SQL query based on a table named 'uploaded_data'. "
              f"The table has the following columns: {column_names}. "
              f"Question: {nlp_question}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except openai.error.AuthenticationError:
        return "Error: Incorrect OpenAI API Key. Please check your key."

# Gradio UI
file_upload = gr.File(label="Upload CSV File")
nlp_input = gr.Textbox(label="Ask a question in Natural Language")
output_text = gr.Textbox(label="Generated SQL Query")
schema_output = gr.Textbox(label="Dataset Schema")

with gr.Blocks() as app:
    gr.Markdown("# SQL Query Generator from Natural Language")
    with gr.Row():
        file_button = gr.Button("Upload & Create Table")
        schema_button = gr.Button("Show Schema")
    
    with gr.Row():
        file_upload.render()
        nlp_input.render()
        query_button = gr.Button("Generate SQL Query")
    
    file_button.click(create_table_from_csv, inputs=[file_upload], outputs=schema_output)
    schema_button.click(show_schema, inputs=[file_upload], outputs=schema_output)
    query_button.click(generate_sql_query, inputs=[file_upload, nlp_input], outputs=output_text)
    
    schema_output.render()
    output_text.render()

app.launch()
