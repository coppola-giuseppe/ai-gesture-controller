# ✋ AI Gesture Volume Control (WIP)

> **Work In Progress (WIP):** Questo progetto è in fase di sviluppo attivo. La funzionalità base di controllo del volume tramite gesture è operativa, ma sono in cantiere nuove funzionalità e gesture per il controllo del desktop.

Un sistema leggero ed efficiente in Python che permette di controllare il volume di sistema tramite gesture delle mani riprese dalla webcam, sfruttando **MediaPipe** per l'AI tracciamento e **PulseAudio/PipeWire** per la gestione audio su Linux.

Può essere eseguito sia con un'interfaccia visiva per il debug sia in modalità **headless** in background.

---

## 🚀 Caratteristiche Principali

* **Rilevamento Pinch Intelligente:** Unisce pollice e indice per attivare il controllo volume. Per evitare attivazioni accidentali, la modifica del volume si sblocca dopo 1 secondo di posizionamento statico.
* **Modifica Proporzionale del Volume:** Muovi la mano verso l'alto o verso il basso per alzare o abbassare il volume con sensibilità dinamica.
* **Modalità Doppia (`VIDEO` / `HEADLESS`):**
  * `VIDEO`: Mostra la finestra video in tempo reale con lo scheletro della mano (landmarks) tracciato.
  * `HEADLESS`: Silenzioso e leggero, gira in background consumando meno risorse.
* **Gestione Eccezioni e Resilienza:** Riconnessione e gestione automatica di disconnessioni webcam o riavvii del server audio PipeWire/PulseAudio.
* **Lock Multi-mano:** Se rileva più mani nel campo visivo, aggancia la prima mano che esegue il gesto ignorando interferenze.

---

## 🛠️ Requisiti di Sistema

* **Sistema Operativo:** Linux (testato su Nobara/Fedora con PipeWire) (WIP per compatibilità Linux/Windows)
* **Python:** 3.9 o superiore
* **Webcam** funzionante

---

## 📦 Installazione

1. **Clona la repository:**
  ```bash
  git clone https://github.com/coppola-giuseppe/ai-gesture-controller.git
  ```

2. **Crea e attiva un ambiente virtuale (consigliato)**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

3. **Installa le dipendenze**
  ```bash
  pip install -r requirements.txt
  ```

4. **Scarica il modello MediaPipe (HandLandmarker):**
  ```bash
  wget -q https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task
  ```

---

## 🚀 Avvio

Assicurati che l'ambiente virtuale sia attivo ed esegui lo script:

  ```bash
  source venv/bin/activate
  python ai_gesture_recognition.py
  ```


---

## ⚙️ Configurazione e Variabili Globali

### Costanti di Configurazione
Puoi modificare queste variabili in cima allo script per adattare il programma al tuo setup:

| Variabile | Tipo / Default | Descrizione |
| :--- | :--- | :--- |
| `MODALITA` | `VIDEO` | `VIDEO` mostra la finestra con i landmark tracciati; `HEADLESS` esegue lo script in background. |
| `CAMERA_INDEX` | `0` | Indice della webcam di sistema da utilizzare (`0` è la webcam integrata/principale). |
| `FRAME_WIDTH` / `HEIGHT` | `1280`x`720` | Risoluzione di acquisizione inviata dall'hardware della webcam. |
| `FPS` | `30` | Frequenza di campionamento dei fotogrammi al secondo. |
| `CHANGE_VOLUME_ON_ALL_OUTPUTS` | `True` | Se `True`, applica il cambio di volume a tutte le schede audio/sink attive su PulseAudio/PipeWire. |
| `LOG` | `True` | Abilita o disabilita i messaggi di debug stampati a terminale. |
| `MARGINE` | `0.05` | Margine della webcam non considerato per le rilevazioni
| `TOLLERANZA_RILEVATO_SEC` | `1.0` | Secondi dopo i quali un gesto è considerato valido
| `TOLLERANZA_RILASCIO_SEC` | `0.3` | Secondi dopo i quali un gesto è considerato concluso