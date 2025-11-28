from flask import Flask, jsonify, render_template, request, redirect, url_for
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app import db
from app.models import Comment


MODEL_DIR = "./app/model"  # Folder tempat model IndoBERT Anda berada
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

# Fungsi Analisis Sentimen menggunakan IndoBERT
def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment = torch.argmax(probs, dim=-1).item()
    return "Positive" if sentiment == 1 else "Negative"

def tambahKomen():
    if request.method == "POST":
        comment_text = request.form["comment"]
        
        # Analisis Sentimen dengan IndoBERT
        sentiment = predict_sentiment(comment_text)
        
        # Simpan ke database
        new_comment = Comment(text=comment_text, sentiment=sentiment)
        db.session.add(new_comment)
        db.session.commit()
        
        return redirect(url_for('home')) 

def tambahKomenApi():
    # Pastikan request memiliki konten JSON
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400
    
   
    data = request.get_json()
    comment_text = data.get("comment")
    
    if not comment_text:
        return jsonify({"error": "Comment text is required"}), 400
    
    try:
        
        sentiment = predict_sentiment(comment_text)
        
       
        new_comment = Comment(text=comment_text, sentiment=sentiment)
        db.session.add(new_comment)
        db.session.commit()
        
        
        return jsonify({
            "message": "Comment added successfully",
            "data": {
                "comment": comment_text,
                "sentiment": sentiment
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500