import os
import sys
import sounddevice as sd
import queue
import subprocess
import tempfile
import wave
import threading
from piper import PiperVoice
import google.generativeai as genai
from settings.settings import IA_NAME, VOICE_PATH, MODEL_PATH, SAMPLE_RATE, BLOCK_SIZE
from dotenv import load_dotenv
import re
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
load_dotenv()

recording_enabled = True
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    global recording_enabled
    if status:
        print(status, file=sys.stderr)
    if recording_enabled:  # ← Vérifier le flag
        audio_queue.put(bytes(indata))

def player_worker(q: "queue.Queue[str | None]"):
    global recording_enabled
    while True:
        path = q.get()
        if path is None:
            return
        recording_enabled = False  # ← Désactiver pendant la lecture
        subprocess.run(["mpv", "--no-terminal", "--really-quiet", path])
        recording_enabled = True   # ← Réactiver après
        try:
            os.remove(path)
        except OSError:
            pass


def clear_screen():
    # Nettoyer le terminal pour une meilleure expérience visuelle
    os.system('cls' if os.name == 'nt' else 'clear')

def get_api_key():
    # Tente de récupérer la clé depuis les variables d'environnement
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    print("=== Configuration de la clé API Gemini ===")
    print("Vous pouvez également définir la variable d'environnement GEMINI_API_KEY pour éviter cette étape.\n")
    while True:
        api_key = input("Veuillez entrer votre clé API Google Gemini : ").strip()
        if api_key:
            return api_key
        print("La clé ne peut pas être vide. Veuillez réessayer.")


def tts_worker(text_q, out_q, voice):
    while True:
        fragment = text_q.get()
        if fragment is None:
            out_q.put(None)  # propage l'arrêt au lecteur
            return
        fd, path = tempfile.mkstemp(prefix="tts_", suffix=".wav")
        os.close(fd)
        with wave.open(path, "wb") as wav_file:
            voice.synthesize_wav(fragment, wav_file)
        out_q.put(path)

def detect_command(response_text):
    resultat = re.search(r"(?mi)^command:\s*(.+)$", response_text)

    if resultat:
        commande = resultat.group(1).strip()
        return resultat.start(), commande
    return None

def execute_command(commande):
    if commande:
        subprocess.run(commande, shell=True)

def gemini():
    clear_screen()
    print("==================================================")
    print("       🤖 BIENVENUE SUR VOTRE GEMINI CHATBOT      ")
    print("==================================================")
    
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model_name = IA_NAME
    
    print("\n==================================================")
    print("        ⚙️ CONFIGURATION DU CONTEXTE DE DÉPART    ")
    print("==================================================")
    print("Définissez le rôle, la personnalité ou le contexte de votre chatbot.")
    print("Exemple : 'Tu es un expert en programmation Python cynique mais d'une grande aide.'")
    print("Laissez vide pour le comportement par défaut d'un assistant utile.\n")

    with open("settings/personality.txt", "r", encoding="utf-8") as f:
        content = f.read()
    system_instruction = content 
    if not system_instruction:
        system_instruction = "Tu es un assistant virtuel utile, amical et précis. Réponds toujours en français."
        print(f"-> Contexte par défaut appliqué : \"{system_instruction}\"")
    else:
        print(f"-> Contexte personnalisé appliqué avec succès !")

    print("\nInitialisation du modèle...")
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        chat = model.start_chat(history=[])
    except Exception as e:
        print(f"Erreur lors de l'initialisation du modèle : {e}")
        sys.exit(1)

    voice = PiperVoice.load(VOICE_PATH)
    print("voice init success")

    print("Initialisation VOSK")
    print("VOSK load")
    SetLogLevel(-1)

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    clear_screen()
    print("==================================================")
    print("             💬 CHAT INITIALISÉ AVEC SUCCÈS        ")
    print("==================================================")
    print(f"Modèle utilisé  : {model_name}")
    print(f"Contexte système: \"{system_instruction}\"")
    print("--------------------------------------------------")
    print("Instructions :")
    print(" - Tapez votre message et appuyez sur Entrée.")
    print(" - Écrivez 'exit', 'quit' ou 'quitter' pour fermer le chat.")
    print(" - Écrivez 'clear' pour vider l'écran du terminal.")
    print("==================================================\n")

    audio_q: "queue.Queue[str | None]" = queue.Queue()
    tts_text_q: "queue.Queue[str | None]" = queue.Queue()

    t_tts = threading.Thread(target=tts_worker, args=(tts_text_q, audio_q, voice), daemon=True)
    t_tts.start()
    t = threading.Thread(target=player_worker, args=(audio_q,), daemon=True)
    t.start()

    one_use = False

    with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            callback=callback,
    ):
        while True:
            try:
                data = audio_queue.get()
                audio_q: "queue.Queue[str | None]" = queue.Queue()
                if rec.AcceptWaveform(data) and one_use == False:
                    one_use = True
                    result = json.loads(rec.Result())
                    user_input = result.get("text", "").strip()
                    if not user_input:
                        continue
                    if user_input.lower() in ['exit', 'quit', 'quitter']:
                        print("\n Assistant : Au revoir ! Passez une excellente journée.")
                        break
                        
                    if user_input.lower() == 'clear':
                        clear_screen()
                        print("==================================================")
                        print("             CONVERSATION EN COURS             ")
                        print("================================================--\n")
                        continue

                    print("Vous", user_input)
                    print(" Assistant : ", end="", flush=True)
                    response = chat.send_message(user_input, stream=True)

                    streamed_text = ""
                    spoken_upto = 0
                    command_start = None
                    
                    for chunk in response:
                        chunk_text = getattr(chunk, "text", "")
                        if not chunk_text:
                            continue

                        print(chunk_text, end="", flush=True)
                        streamed_text += chunk_text

                        if command_start is None:
                            command_match = detect_command(streamed_text)
                            if command_match:
                                command_start, commande = command_match
                                print(f"\nCommande détectée : {commande}")
                                run_command = threading.Thread(target=execute_command, args=(commande,), daemon=True)
                                run_command.start()

                        safe_upto = command_start if command_start is not None else max(streamed_text.rfind(c) for c in ".!?:") + 1
                        if safe_upto > spoken_upto:
                            tts_fragment = streamed_text[spoken_upto:safe_upto]
                            if tts_fragment.strip():
                                tts_text_q.put(tts_fragment)
                            spoken_upto = safe_upto
                    print("\n")
                    
            except KeyboardInterrupt:
                print("\n\n Assistant : Chat interrompu. Au revoir !")
                audio_q.put(None)
                t.join()
                break
            except Exception as e:
                print(f"\nUne erreur est survenue lors de la communication avec l'API : {e}\n")
                audio_q.put(None)
                t.join()
                break

if __name__ == "__main__":
    gemini()
