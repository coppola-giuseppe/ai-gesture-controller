import cv2
import mediapipe as mp
import time
import math
import pulsectl

# VARIABILI DI STATO    

# Se impostata su 'VIDEO' appare l'interfaccia grafica che mostra i landmarks in tempo reale
# Se impostata su 'HEADLESS' gira in background senza interfaccia grafica
MODALITA = 'HEADLESS'

LOG = False # Se impostata su True stampa i log durante i passaggi altrimenti no. Le eccezioni vengono stampate sempre.

CAMERA_INDEX = 0           # 0 per la webcam principale, 1 per una eventuale seconda webcam
FRAME_WIDTH = 1280         # Larghezza risoluzione webcam
FRAME_HEIGHT = 720         # Altezza risoluzione webcam
FPS = 30                   # FPS per la frequenza di lettura

MARGINE = 0.05 # indica il margine (da 0.0 a 1.0) della webcam che non viene considerato per le rilevazioni

TOLLERANZA_RILEVATO_SEC = 1.0 # indica dopo quanti secondi che un gesto è rilevato costantemente il sistema registra l'effettivo gesto
TOLLERANZA_RILASCIO_SEC = 0.3 # indica dopo quanti secondi che non viene rilevato un gesto il sistema registra l'effettiva mancanza di gesti

CHANGE_VOLUME_ON_ALL_OUTPUTS = True # True: cambia il valore audio di tutti gli output, False: cambia il valore audio dell'output predefinito

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

CONNESSIONI_MANO = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Pollice
    (0, 5), (5, 6), (6, 7), (7, 8),        # Indice
    (5, 9), (9, 10), (10, 11), (11, 12),   # Medio
    (9, 13), (13, 14), (14, 15), (15, 16), # Anulare
    (13, 17), (17, 18), (18, 19), (19, 20),# Mignolo
    (0, 17)                                # Palmo
]

def disegna_riferimenti(image, detection_result):
    """Data una immagine {image} ci disegna sopra la deduzione per la mano """
    h, w, _ = image.shape
    if detection_result.hand_landmarks:
        for riferimenti_mano in detection_result.hand_landmarks:
            for connection in CONNESSIONI_MANO:
                p1 = riferimenti_mano[connection[0]]
                p2 = riferimenti_mano[connection[1]]
                pt1 = (int(p1.x * w), int(p1.y * h))
                pt2 = (int(p2.x * w), int(p2.y * h))
                cv2.line(image, pt1, pt2, (0, 255, 0), 2)

            for riferimento in riferimenti_mano:
                cx, cy = int(riferimento.x * w), int(riferimento.y * h)
                cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)
    return image

def calcolo_distanza_3d(p1, p2):
    """ Calcola la distanza in 3 dimensioni da {p1} a {p2}"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

def controllo_margini(image_landmarks, margine=0.05):
    """Controllo che i landmarks sull'immagine non siano troppo vicini al margine della webcam"""
    thumb_tip = image_landmarks[4]
    index_tip = image_landmarks[8]

    if (thumb_tip.x < margine or thumb_tip.x > 1 - margine or 
        thumb_tip.y < margine or thumb_tip.y > 1 - margine or
        index_tip.x < margine or index_tip.x > 1 - margine or 
        index_tip.y < margine or index_tip.y > 1 - margine):
        return False
    return True

def controllo_pinch(world_landmarks, is_already_active):
    """ Controlla se la mano è in "pinch" """
    wrist = world_landmarks[0]
    thumb_tip = world_landmarks[4]
    index_tip = world_landmarks[8]
    middle_tip = world_landmarks[12]
    
    index_mcp = world_landmarks[5]
    middle_mcp = world_landmarks[9] 
    pinky_mcp = world_landmarks[17]

    palmo_larghezza = calcolo_distanza_3d(index_mcp, pinky_mcp)
    palmo_lunghezza = calcolo_distanza_3d(wrist, middle_mcp)
    
    scala_mano = max(palmo_larghezza, palmo_lunghezza)
    
    if scala_mano < 0.02: 
        return False

    distanza_pollice_indice = calcolo_distanza_3d(thumb_tip, index_tip)
    dist_polso_medio_punta = calcolo_distanza_3d(wrist, middle_tip)
    stato_pugno = dist_polso_medio_punta < (palmo_lunghezza * 0.8)

    soglia_pinch = scala_mano * 0.40 if is_already_active else scala_mano * 0.25
    return (distanza_pollice_indice < soglia_pinch) and not stato_pugno


# Inizializzo il client di PulseWire
pulse = pulsectl.Pulse('volume-gesture-control')
ultimo_volume = -1.0

def volume_attuale():
    """ Prendo il volume attuale del dispositivo predefinito del sistema """
    try:
        server_info = pulse.server_info()
        default_sink = pulse.get_sink_by_name(server_info.default_sink_name)
        if default_sink:
            return sum(default_sink.volume.values) / len(default_sink.volume.values)
    except Exception as e:
        if LOG: print(f"Errore lettura volume: {e}")
    return 0.5 



def volume_handler(volume_target):
    """
    Imposta il volume in base a {volume_target}, se la variabile globale {CHANGE_VOLUME_ON_ALL_OUTPUTS} è settata su True imposta il volume su tutti gli output, altrimenti solo su quello predefinito
    """

    if CHANGE_VOLUME_ON_ALL_OUTPUTS:
        try:
            for sink in pulse.sink_list():
                pulse.volume_set_all_chans(sink, volume_target)
                if LOG: print(f"[{sink.description}] -> Volume impostato al {int(volume_target * 100)}%")
        except Exception:
            pass

    else:
        try:
            server_info = pulse.server_info()
            default_sink = pulse.get_sink_by_name(server_info.default_sink_name)
            
            if default_sink:
                pulse.volume_set_all_chans(default_sink, volume_target)
                if LOG: print(f"[{default_sink.description}] -> Volume impostato al {int(volume_target * 100)}%")
        except Exception:
            pass


options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)

try:
    with HandLandmarker.create_from_options(options) as landmarker:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise RuntimeError(f"Impossibile aprire la webcam di indice {CAMERA_INDEX}.")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)

        
        gesto_globale = None  # mi salvo il gesto attualmente in corso
        last_timestamp_ms = -1
        
        
        tempo_ultimo_rilevamento = 0
        
        
        mano_in_uso = None # mi salvo la mano che attualmente sta facendo un segno riconosciuto

        # variabili per la logica della gestione pinch-volume
        pinch_timer = 0
        pinch_confermato = False
        y_iniziale = 0.0
        volume_iniziale = 0.5

        if MODALITA == 'HEADLESS':
            if LOG: print("Script avviato in modalità HEADLESS (background). Premi Ctrl+C per uscire.")

        while cap.isOpened():
            ret, image = cap.read()
            if not ret:
                if LOG: print("Ignoro eventuali frame vuoti dalla webcam.")
                break

            
            image.flags.writeable = False # rendo non scrivibile il frame per velocizzare le operazioni
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
            image.flags.writeable = True 
            
            timestamp_ms = int(time.time() * 1000)
            if timestamp_ms <= last_timestamp_ms:
                timestamp_ms = last_timestamp_ms + 1
            last_timestamp_ms = timestamp_ms

            risultati = landmarker.detect_for_video(mp_image, timestamp_ms)

            gesto_in_questo_frame = None
            pinch_y = None

            # uso la funzione zip per discriminare la mano
            if risultati.hand_world_landmarks and risultati.hand_landmarks and risultati.handedness:
                for world_landmarks, image_landmarks, handedness in zip(risultati.hand_world_landmarks, risultati.hand_landmarks, risultati.handedness):
                    
                    identificativo_mano = handedness[0].category_name
                    
                    # se un gesto è già in corso, ignoro eventuali altre mani
                    if gesto_globale is not None and mano_in_uso != identificativo_mano:
                        continue

                    # controllo di essere entro i margini
                    if not controllo_margini(image_landmarks, MARGINE):
                        continue

                    # setto il gesto attuale come "pinch"
                    is_pinch_active = (gesto_globale == "PINCH")
                    if controllo_pinch(world_landmarks, is_pinch_active):
                        gesto_in_questo_frame = "PINCH"
                        pinch_y = image_landmarks[8].y
                        mano_in_uso = identificativo_mano # Setto la mano in uso per ignorare altre mani
                        break 


            
            if gesto_in_questo_frame == "PINCH":
                tempo_ultimo_rilevamento = time.time() # controllo temporale per la verifica dell'uscita dallo stato "pinch"
                
                # setto il gesto in corso come il "pinch" e aggiorno le variabili
                if gesto_globale != "PINCH":
                    gesto_globale = "PINCH"
                    pinch_timer = time.time()
                    pinch_confermato = False
                    if LOG: print(f"Gesto di Pinch rilevato ({mano_in_uso})! Mantenere per {TOLLERANZA_RILEVATO_SEC} secondo/i...")

                # per filtrare gli errori aspetto che il gesto rimanga "pinch" per almeno {TOLLERANZA_RILEVATO_SEC} secondo 
                if not pinch_confermato and (time.time() - pinch_timer >= TOLLERANZA_RILEVATO_SEC):
                    pinch_confermato = True
                    y_iniziale = pinch_y
                    volume_iniziale = volume_attuale()
                    if LOG: print("Controllo volume SBLOCCATO! Muovi la mano su o giù.")
                
                if pinch_confermato:
                    # calcolo della posizione relativa della mano rispetto all'inizio del "pinch"
                    delta_y = y_iniziale - pinch_y
                    sensibilita = 2.5 # sensibilità del movimento, aumentandola ad un movimento della mano corrisponde un aumento di volume maggiore
                    
                    volume_calcolato = volume_iniziale + (delta_y * sensibilita)
                    volume_calcolato = max(0.0, min(1.0, volume_calcolato)) # controllo che il volume rimanga nei limiti 0.0-1.0

                    # chiamo l'handler per cambiare il volume solo se l'effettivo cambio di volume è significativo
                    if abs(volume_calcolato - ultimo_volume) > 0.02:
                        volume_handler(volume_calcolato)
                        ultimo_volume = volume_calcolato

            else:
                # se non rilevo nessun gesto per {TOLLERANZA_RILASCIO_SEC} secondi, setto il gesto attuale come nessuno
                if gesto_globale is not None:
                    if (time.time() - tempo_ultimo_rilevamento) > TOLLERANZA_RILASCIO_SEC:
                        if LOG: print(f"Gesto {gesto_globale} rilasciato!") 
                        gesto_globale = None
                        pinch_confermato = False 
                        mano_in_uso = None # levo il lock della mano che era utilizzata per permettere anche all'altra di eseguire gesti

            if MODALITA == 'VIDEO':
                immagine_riferimento = disegna_riferimenti(image, risultati)
                cv2.imshow('MediaPipe Hands', cv2.flip(immagine_riferimento, 1))

                # per chiudere la grafica si deve premere ESC
                if cv2.waitKey(1) & 0xFF == 27:
                    break

except KeyboardInterrupt:
    print("\nInterruzione manuale dello script.")
except cv2.error as e:
    print(f"\nErrore critico di OpenCV: {e}")
except Exception as e:
    print(f"\nErrore critico nel ciclo principale: {e}")

finally:

    if cap is not None and cap.isOpened():
        cap.release()
    if MODALITA == 'VIDEO':
        cv2.destroyAllWindows()
    try:
        pulse.close()
    except Exception:
        pass
    if LOG: print("Terminazione corretta!")