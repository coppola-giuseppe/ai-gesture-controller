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

* **Sistema Operativo:** Linux (testato su Nobara/Fedora con PipeWire)
* **Python:** 3.9 o superiore
* **Webcam** funzionante

---

## 📦 Installazione

1. **Clona la repository:**
   ```bash
   git clone [https://github.com/coppola-giuseppe/ai-gesture-controller](https://github.com/coppola-giuseppe/ai-gesture-controller)
   ai-gesture-controller
