# Witana Pulse Insight Assistant

Et proof-of-concept som viser hvordan AI kan brukes til å analysere energidata og teknisk dokumentasjon for bygg.

## Hva det gjør

- **Energioversikt** – viser daglig energiforbruk opp mot forventet nivå
- **Avviksanalyse** – oppdager dager med unormalt høyt forbruk og forklarer hva som sannsynligvis skjedde
- **Rapportgenerator** – lager automatiske rapportutkast og energiprediksjoner
- **Dokumentassistent** – still spørsmål til et teknisk dokument du limer inn

---

## Slik kjører du det

### 1. Installer Python
Last ned og installer Python fra [python.org](https://www.python.org/downloads/) hvis du ikke har det.

### 2. Skaff en gratis Groq API-nøkkel
Gå til [console.groq.com](https://console.groq.com), opprett en konto og lag en API-nøkkel.

### 3. Last ned prosjektet
Klikk den grønne **Code**-knappen på denne siden og velg **Download ZIP**. Pakk ut mappen.

### 4. Installer avhengigheter
Åpne terminalen (søk på "PowerShell" i Start-menyen), naviger til mappen og kjør:

```
pip install -r requirements.txt
```

### 5. Start appen

```
$env:GROQ_API_KEY = "lim-inn-din-nøkkel-her"
python app.py
```

### 6. Åpne i nettleseren
Gå til [http://localhost:5000](http://localhost:5000)

---

> Dataene i appen er syntetiske og kun ment for demonstrasjon.
