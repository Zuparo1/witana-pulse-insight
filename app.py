import os
import json
from flask import Flask, render_template, request, jsonify, session
from data_generator import generate_energy_data, get_daily_summary
from ai_engine import (
    analyze_energy_anomaly, generate_monthly_report,
    document_chat, predict_next_week
)

app = Flask(__name__)
app.secret_key = "witana-pulse-poc-2026"

# Pre-generate data once at startup
HOURLY_DATA = generate_energy_data(days=30)
DAILY_DATA = get_daily_summary(HOURLY_DATA)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/energy/daily")
def api_daily():
    return jsonify(DAILY_DATA)

@app.route("/api/energy/anomalies")
def api_anomalies():
    anomaly_days = [d for d in DAILY_DATA if d["deviation_pct"] > 15]
    return jsonify(anomaly_days)

@app.route("/api/analyze-anomaly", methods=["POST"])
def api_analyze_anomaly():
    data = request.json
    day = next((d for d in DAILY_DATA if d["date"] == data["date"]), None)
    if not day:
        return jsonify({"error": "Dato ikke funnet"}), 404

    analysis = analyze_energy_anomaly(
        building="Bygg A - Kontorbygg Hamar",
        date=day["date"],
        weekday=day["weekday"],
        actual_kwh=day["total_kwh"],
        expected_kwh=day["expected_kwh"],
        deviation_pct=day["deviation_pct"],
        avg_temp=day["avg_temp"],
        anomaly_hours=day["anomaly_hours"],
        anomalies=day["anomalies"],
    )
    return jsonify({"analysis": analysis})

@app.route("/api/monthly-report", methods=["POST"])
def api_monthly_report():
    report = generate_monthly_report(
        building="Bygg A - Kontorbygg Hamar",
        month="Mai 2026",
        daily_data=DAILY_DATA,
    )
    return jsonify({"report": report})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    prediction = predict_next_week(
        building="Bygg A - Kontorbygg Hamar",
        daily_data=DAILY_DATA,
    )
    return jsonify({"prediction": prediction})

@app.route("/api/document-chat", methods=["POST"])
def api_document_chat():
    data = request.json
    if not data.get("document") or not data.get("question"):
        return jsonify({"error": "Mangler dokument eller spørsmål"}), 400

    if "chat_history" not in session:
        session["chat_history"] = []

    answer = document_chat(
        document_text=data["document"],
        question=data["question"],
        history=session["chat_history"][-4:],  # Keep last 4 turns
    )

    session["chat_history"] = session.get("chat_history", []) + [
        {"question": data["question"], "answer": answer}
    ]
    session.modified = True

    return jsonify({"answer": answer})

@app.route("/api/document-chat/reset", methods=["POST"])
def api_reset_chat():
    session["chat_history"] = []
    return jsonify({"ok": True})

if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("\n⚠  Set GROQ_API_KEY environment variable before starting.\n")
    app.run(debug=True, port=5000)
