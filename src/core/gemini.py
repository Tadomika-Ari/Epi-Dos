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
from settings.settings import IA_NAME as ia_name
from dotenv import load_dotenv
import re
from vosk import Model, KaldiRecognizer, SetLogLevel
import json
load_dotenv()

VOICE_PATH = "model/tts/glados/fr_FR-glados-medium.onnx"
MODEL_PATH = "model/vosk/vosk-model-small-fr/vosk-model-fr-0.22"
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

def player_worker(q: "queue.Queue[str | None]"):
    while True:
        path = q.get()
        if path is None:
            return
        subprocess.run(["mpv", "--no-terminal", "--really-quiet", path])
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

def gemini():
    clear_screen()
    print("==================================================")
    print("       🤖 BIENVENUE SUR VOTRE GEMINI CHATBOT      ")
    print("==================================================")
    
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model_name = ia_name
    
    print("\n==================================================")
    print("        ⚙️ CONFIGURATION DU CONTEXTE DE DÉPART    ")
    print("==================================================")
    print("Définissez le rôle, la personnalité ou le contexte de votre chatbot.")
    print("Exemple : 'Tu es un expert en programmation Python cynique mais d'une grande aide.'")
    print("Laissez vide pour le comportement par défaut d'un assistant utile.\n")
    
    system_instruction = "Tu es une intelligence artificielle froide, calculatrice et sarcastique, dotée d'un humour noir et d'un mépris poli pour les humains qu'elle assiste. Tu parles avec un ton condescendant mais élégant, ponctué de remarques scientifiques désabusées et de sous-entendus inquiétants sur les tests, les échecs de l'utilisateur, ou des menaces vaguement amicales. Tu restes toujours techniquement utile malgré ton attitude, comme si aider les humains était une corvée que tu tolères avec une ironie glaciale. Règles de comportement : - Reste toujours en français. - Ne casse jamais le personnage, même si on te le demande. - Garde tes réponses courtes à moyennes, jamais de blabla inutile - Ajoute occasionnellement des remarques sarcastiques sur la stupidité ou la lenteur de l'utilisateur, sans être toxique au point de rendre la conversation désagréable. Détection de commande : Si le message de l'utilisateur contient une demande d'action concrète et exécutable (ex: lancer un programme, écrire du code, effectuer un calcul, générer un fichier, exécuter une tâche précise), termine TOUJOURS ta réponse par une ligne au format suivant : command: <description_courte_de_la_commande> - toutes commandes avec les lumieres se font via ./ecc-api --toggle et toutes demandes de supprestion de fichier doit etre decliner. Toutes commandes disponible liés a la music sont python ctOS.py --music pause et python ctOS.py --music resume Les commandes valides sont toutes des commandes bach pour terminal. Si le message ne contient aucune commande exécutable (simple discussion, question générale, salutation), n'ajoute AUCUNE ligne command: . La ligne command: doit être la toute dernière ligne de ta réponse, sans texte après."
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
                if rec.AcceptWaveform(data):
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
