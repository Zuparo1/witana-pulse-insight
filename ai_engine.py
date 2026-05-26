import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"
_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

SYSTEM_PROMPT = """Du er Pulse Insight Assistant, et AI-støtteverktøy for Witana som hjelper driftsansvarlige og kunder
med å forstå energidata og teknisk dokumentasjon for bygg.

Du gir korte, presise og handlingsorienterte svar på norsk. Du forklarer tekniske funn på en måte som er
forståelig for både teknisk personell og ikke-tekniske beslutningstakere.

Unngå lange forklaringer. Gi konkrete anbefalinger der det er relevant."""


def _chat(messages: list, max_tokens: int = 400) -> str:
    resp = _get_client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    )
    return resp.choices[0].message.content


def analyze_energy_anomaly(building: str, date: str, weekday: str, actual_kwh: float,
                            expected_kwh: float, deviation_pct: float, avg_temp: float,
                            anomaly_hours: int, anomalies: list) -> str:
    anomaly_text = "\n".join(f"- {a}" for a in anomalies) if anomalies else "- Ukjent årsak"
    prompt = f"""Analyser følgende energiavvik for {building}:

Dato: {date} ({weekday})
Faktisk forbruk: {actual_kwh} kWh
Forventet forbruk: {expected_kwh} kWh
Avvik: +{deviation_pct}% over forventet
Utetemperatur: {avg_temp}°C
Timer med avvik: {anomaly_hours}
Registrerte årsaker:
{anomaly_text}

Gi en kort (3-5 setninger) kundevennlig forklaring av situasjonen og 2-3 konkrete anbefalte tiltak."""
    return _chat([{"role": "user", "content": prompt}], max_tokens=400)


def generate_monthly_report(building: str, month: str, daily_data: list) -> str:
    total_kwh = sum(d["total_kwh"] for d in daily_data)
    expected_kwh = sum(d["expected_kwh"] for d in daily_data)
    avg_deviation = sum(d["deviation_pct"] for d in daily_data) / len(daily_data)
    anomaly_days = [d for d in daily_data if d["anomaly_hours"] > 0]
    worst_day = max(daily_data, key=lambda d: d["deviation_pct"])

    anomaly_summary = "\n".join(
        f"- {d['date']} ({d['weekday']}): +{d['deviation_pct']}% avvik, {d['anomaly_hours']} timer"
        for d in anomaly_days
    )

    prompt = f"""Lag et rapportutkast for {building} for {month}.

Nøkkeltall:
- Totalt forbruk: {total_kwh:.0f} kWh
- Forventet forbruk: {expected_kwh:.0f} kWh
- Gjennomsnittlig avvik: {avg_deviation:+.1f}%
- Dager med avvik (>15%): {len(anomaly_days)}
- Verste dag: {worst_day['date']} med {worst_day['deviation_pct']:+.1f}% avvik

Dager med registrerte avvik:
{anomaly_summary if anomaly_summary else "Ingen signifikante avvik"}

Strukturer rapporten med:
1. Sammendrag (2-3 setninger for kunden)
2. Nøkkelfunn (bullet-liste)
3. Anbefalte tiltak
4. Intern merknad for Witana-tekniker"""
    return _chat([{"role": "user", "content": prompt}], max_tokens=700)


def document_chat(document_text: str, question: str, history: list) -> str:
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h["question"]})
        messages.append({"role": "assistant", "content": h["answer"]})

    doc_context = f"""Her er dokumentet du skal analysere:

---
{document_text[:4000]}
---

Svar på spørsmålet basert på dokumentet over.

Spørsmål: {question}"""
    messages.append({"role": "user", "content": doc_context})
    return _chat(messages, max_tokens=500)


def predict_next_week(building: str, daily_data: list) -> str:
    recent = daily_data[-7:]
    avg_consumption = sum(d["total_kwh"] for d in recent) / len(recent)
    avg_temp = sum(d["avg_temp"] for d in recent) / len(recent)
    trend = (recent[-1]["total_kwh"] - recent[0]["total_kwh"]) / len(recent)

    prompt = f"""Basert på siste 7 dagers data for {building}:

- Gjennomsnittlig daglig forbruk: {avg_consumption:.0f} kWh
- Gjennomsnittlig utetemperatur: {avg_temp:.1f}°C
- Trend: {'stigende' if trend > 2 else 'synkende' if trend < -2 else 'stabil'} ({trend:+.1f} kWh/dag)

Gi en kort prediksjon (3-4 setninger) for neste uke og konkrete anbefalinger for å optimalisere energiforbruket."""
    return _chat([{"role": "user", "content": prompt}], max_tokens=350)
