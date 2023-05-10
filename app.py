#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase
import spacy
import pandas as pd
import re


app = Flask(__name__)

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Set up the Neo4j driver
driver = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "projects"))


# In[2]:


def determine_question_type(nlp_question):
    from spacy.lang.en import English

    nlp = English()
    doc = nlp_question
    print(doc)
    question_type = "unknown"
    
   
    # Identify Type 1 questions
    if any((token.text in {"diseases"}) for token in doc):
        if "related" in [token.text for token in doc]:
            question_type = "Type 1"
        elif "cause" in [token.text for token in doc]:
            question_type = "Type 1"
     # Identify Type 1 questions
    elif any((token.text in {"antibiotics", "drug"}) for token in doc):
        question_type = "Type 2"
                
    elif "causes" in [token.text for token in doc] and "risk" in [token.text for token in doc]:
        question_type = "Type 3"
            
    return question_type


# In[3]:


def generate_cypher_query(nlp_question,q_type):
        doc = nlp(nlp_question)
        cypher_query = ""
        # Read the Excel file
        df = pd.read_csv("final_diseases_dataset_v2.csv")

        # Create an empty list to store the unique entries
        First_Item_Name = []
        Second_Item_Name = []

        # Iterate over each column in the DataFrame
        for col in df.columns:
            # Iterate over each value in the column
            for value in df['First_Item_Name']:
                # Check if the value is not already in the unique list
                if value not in First_Item_Name:
                    # If the value is unique, add it to the list
                    First_Item_Name.append(value)
            # Iterate over each value in the column
            for value in df['Second_Item_Name']:
                # Check if the value is not already in the unique list
                if value not in Second_Item_Name:
                    # If the value is unique, add it to the list
                    Second_Item_Name.append(value)


        # Define regular expressions for the target words
        regexes = [re.compile(fr'{word}', re.IGNORECASE) for word in Second_Item_Name]
        print(Second_Item_Name)
      
       # Find matching words in Second_Item_Name
        matches = []
        for regex in regexes:
            match = regex.search(nlp_question)
            if match:
                matches.append(regex.pattern)


        print(matches)
        first_item_name_ = ''
        second_item_name_ = ''
        # Get the first and second item names
        for i in range(len(matches)):
            if i == 0:
                first_item_name_ = matches[0]
            elif i == 1:
                second_item_name_ = matches[1]

                

        print("first_item_name_ = " + first_item_name_)
        print("second_item_name_ = " + second_item_name_)
        
        
        if q_type == "Type 1":
            cypher_query = f"MATCH (e:First_Item)-[r:Relation]->(c:Second_Item) WHERE c.Name =~ '{first_item_name_}' OPTIONAL MATCH (e)<-[r_inv:InverseRelation]-(c) RETURN e, r, c, r_inv"
            print("Type 1",cypher_query)
        elif q_type == "Type 2":
            cypher_query = f"MATCH (e:First_Item)-[r:Relation]->(c:Second_Item) WHERE c.Name =~ '{first_item_name_}' MATCH (e)-[dr:Relation]->(f) WHERE f.Name =~ '{second_item_name_}' RETURN e, r, c, dr, f"
            print("Type 2",cypher_query)
        elif q_type == "Type 3":
            cypher_query = f"""MATCH (n:First_Item)-[r:Relation{{type: "may cause"}}]->(c:Second_Item) WHERE c.Name =~ "{first_item_name_}" MATCH (f)-[dr:Relation{{type: "is a risk factor for"}}]->(c) RETURN n, f, c, r, dr"""

            print("Type 3",cypher_query)
        
        return cypher_query
            
                



# In[ ]:



# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')



# Define the route for the Cypher query - Student
@app.route('/convert_nlp_to_cypher', methods=['POST'])
def stu_query():
    # Get the natural language query from the HTML form
    query_text = request.form.get('nlp_query')
    print("query_text",query_text)
    # Parse the natural language query using spaCy
    doc = nlp(query_text)
    doc_lower = nlp(query_text.lower())
    print("Parse the natural language query using spaCy",doc)
    #determine Question type
    quesType = determine_question_type(doc_lower)
    print("quesType",quesType)
    

    
    
    # Generate Cypher query
    cypher_query = generate_cypher_query(query_text,quesType)
    print(cypher_query)
    # Return the result as a JSON object
    return cypher_query


if __name__ == '__main__':
    app.run(port=8080)


# In[ ]:




