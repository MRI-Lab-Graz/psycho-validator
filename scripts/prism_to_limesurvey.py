#!/usr/bin/env python3
"""
Convert Prism/BIDS JSON sidecar to LimeSurvey Structure File (.lss).

Usage:
    python prism_to_limesurvey.py <input_sidecar.json> [output_structure.lss]

This script allows you to define your questionnaire in a clean JSON format
and automatically generate the importable LimeSurvey structure.
"""

import sys
import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def create_cdata(text):
    """Helper to create CDATA-like text (LimeSurvey uses HTML entities often)"""
    return text if text else ""

def add_row(parent, data):
    """Add a <row> element with child tags based on dictionary"""
    row = ET.SubElement(parent, "row")
    for key, value in data.items():
        child = ET.SubElement(row, key)
        # CDATA handling is tricky in ElementTree, we'll just set text
        # LimeSurvey is usually fine with standard XML escaping
        child.text = str(value)

def json_to_lss(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Filter out metadata keys
    questions = {k: v for k, v in data.items() if k not in ["Technical", "Study", "Metadata", "Categories", "TaskName"]}
    
    # IDs
    sid = "123456" # Dummy Survey ID
    gid = "10"     # Dummy Group ID
    
    # Root element
    root = ET.Element("document")
    ET.SubElement(root, "LimeSurveyDocType").text = "Survey"
    ET.SubElement(root, "DBVersion").text = "366" # Approximate version
    
    # Languages
    langs = ET.SubElement(root, "languages")
    ET.SubElement(langs, "language").text = "en"
    
    # 1. ANSWERS Section (Collect all unique answer sets to generate IDs)
    # We need to generate answer entries for questions with 'Levels'
    answers_elem = ET.SubElement(root, "answers")
    answers_rows = ET.SubElement(answers_elem, "rows")
    
    # 2. QUESTIONS Section
    questions_elem = ET.SubElement(root, "questions")
    questions_rows = ET.SubElement(questions_elem, "rows")
    
    # 3. GROUPS Section
    groups_elem = ET.SubElement(root, "groups")
    groups_rows = ET.SubElement(groups_elem, "rows")
    
    # Add the single group
    add_row(groups_rows, {
        "gid": gid,
        "sid": sid,
        "group_name": data.get("TaskName", "Questionnaire"),
        "group_order": "0",
        "description": "",
        "language": "en",
        "randomization_group": "",
        "grelevance": ""
    })
    
    # Process Questions
    qid_counter = 100
    sort_order = 0
    
    for q_code, q_data in questions.items():
        # Skip if not a dictionary (e.g. extra metadata fields like "Instructions")
        if not isinstance(q_data, dict):
            continue

        qid = str(qid_counter)
        qid_counter += 1
        sort_order += 1
        
        description = q_data.get("Description", q_code)
        levels = q_data.get("Levels", {})
        
        # Determine Type
        # L = List (Radio) - if levels exist
        # T = Long Free Text - if no levels
        q_type = "L" if levels else "T"
        
        # Add Question Row
        add_row(questions_rows, {
            "qid": qid,
            "parent_qid": "0",
            "sid": sid,
            "gid": gid,
            "type": q_type,
            "title": q_code,
            "question": description,
            "other": "N",
            "mandatory": "Y",
            "question_order": str(sort_order),
            "language": "en",
            "scale_id": "0",
            "same_default": "0",
            "relevance": "1"
        })
        
        # Add Answers if applicable
        if levels:
            sort_ans = 0
            for code, answer_text in levels.items():
                sort_ans += 1
                add_row(answers_rows, {
                    "qid": qid,
                    "code": code,
                    "answer": answer_text,
                    "sortorder": str(sort_ans),
                    "language": "en",
                    "assessment_value": "0",
                    "scale_id": "0"
                })

    # 4. SUBQUESTIONS (Empty for now, unless we implement arrays later)
    subquestions_elem = ET.SubElement(root, "subquestions")
    ET.SubElement(subquestions_elem, "rows")

    # 5. SURVEYS Section (General Settings)
    surveys_elem = ET.SubElement(root, "surveys")
    surveys_rows = ET.SubElement(surveys_elem, "rows")
    
    add_row(surveys_rows, {
        "sid": sid,
        "gsid": "1",
        "admin": "Administrator",
        "active": "N",
        "anonymized": "N",
        "format": "G", # Group by Group
        "savetimings": "Y",
        "template": "vanilla",
        "language": "en"
    })
    
    # 6. SURVEY_LANGUAGESETTINGS (Title, etc.)
    surveys_lang_elem = ET.SubElement(root, "surveys_languagesettings")
    surveys_lang_rows = ET.SubElement(surveys_lang_elem, "rows")
    
    add_row(surveys_lang_rows, {
        "surveyls_survey_id": sid,
        "surveyls_language": "en",
        "surveyls_title": data.get("TaskName", "Generated Survey"),
        "surveyls_description": f"Generated from Prism JSON on {datetime.now().isoformat()}",
        "surveyls_welcometext": "",
        "surveyls_endtext": ""
    })

    # Write to file
    tree = ET.ElementTree(root)
    # Indent for readability (Python 3.9+)
    if hasattr(ET, "indent"):
        ET.indent(tree, space="  ", level=0)
        
    tree.write(output_path, encoding="UTF-8", xml_declaration=True)
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prism_to_limesurvey.py <input_sidecar.json> [output_structure.lss]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        sys.exit(1)
        
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        output_path = f"{base_name}.lss"
        
    json_to_lss(json_path, output_path)
