# utils/doc_writer.py
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_BREAK
import logging
import markdown
from bs4 import BeautifulSoup
from io import BytesIO
import editor.utils.db
from flask_login import current_user

def markdown_to_docx_paragraph(doc: Document, input_text: str):
    # Convert markdown to HTML then parse
    html=markdown.markdown(input_text)
    soup = BeautifulSoup(html, 'html.parser')

    for p in soup.find_all(["p"]):

        para=doc.add_paragraph()
        for child in p.contents:
            if child.name == "strong":
                run = para.add_run(child.get_text())
                run.bold = True
            elif child.name == "em":
                run = para.add_run(child.get_text())
                run.italic = True
            elif child.name is None:
                para.add_run(child)
    return para

def insert_image(doc: Document, image_b64: str, mime_type: str) -> None:
    try:
        if mime_type not in ["image/png", "image/jpeg", "image/jpg"]:
            raise ValueError(f"Unsupported MIME type: {mime_type}")

        #img_data = base64.b64decode(image_b64)
        img_io = BytesIO(image_b64)
        doc.add_picture(img_io, height=Inches(4.5))  # or your preferred width

    except Exception as e:
        doc.add_paragraph(f"[Image failed to render: {e}]")

def generate_doc_from_posts(story_id) -> BytesIO:
    posts=editor.utils.db.get_all_posts_raw(story_id)
    logging.debug("Entering print generation")
    doc = Document()
    story = editor.utils.db.get_story(story_id)
    doc.add_heading(f"Title {story['title']}", level=0)
    doc.add_heading(f"Author {current_user.user_name}", level=2)
    if story['note'] != "":
        markdown_to_docx_paragraph(doc, story['note'])

    ix=1
    char_print=False

    for post in posts:

        if post['source']=="post" and post['creator'] != "user":
            title = f"Chapter {ix}"
            ix +=1 
            if char_print:
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
                char_print=False
            doc.add_heading(title, level=2)
        
        if post['creator'] == "model":
            markdown_to_docx_paragraph(doc, post['content'])

        if post['part_type'] == "text":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            doc.add_heading("Character", level=2)
            markdown_to_docx_paragraph(doc, post['part_text'])
            char_print=True
        
        if post['part_image_mime_type'] != "" and post['part_image_mime_type'] != None :  # presence implies image exists
            insert_image(doc, post['part_image_data'], post['part_image_mime_type'])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer