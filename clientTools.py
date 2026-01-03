from networking import *
import piper, subprocess, queue, json
import sounddevice as sd


sd_stream = sd.RawOutputStream(
    samplerate=16000, 
    channels=1, 
    dtype='int16'
)
sd_stream.start()

audioQueue = queue.Queue()

model = r"voices/en_US-danny-low.onnx"
config = r"voices/en_US-danny-low.onnx.json"


piper = subprocess.Popen(
    ["piper",
    "-m", model,
    "-c", config,
    "--rate", "1.3",
    "--output-raw"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE
)


OLLAMA_URL = determineOllamaUrl()
MODEL_NAME = "qwen2.5:14b"





def getResponse(prompt, personality, personalityName):

    '''
    for i in range(10):
        # Send request to Ollama
        response = sendPayload({
            "model": MODEL_NAME,
            "prompt": prompt,
            "personality": personality,
            "personalityName": personalityName
        }, True)
    
        if response is None:
            if i == 9:
                print("WESTLEY: Something went wrong, please try again.")
                return ""
            print("WESTLEY: Something went wrong, atempting again.")
        else:
            break'''
            
    response = sendPayload({
            "model": MODEL_NAME,
            "prompt": prompt,
            "personality": personality,
            "personalityName": personalityName
        }, True)

    # get live output
    out = ""

    for line in response.iter_lines():
        try:
            if line:
                chunk = line.decode('utf-8').removeprefix('data: ')
                if chunk and chunk != "[DONE]":
                    #format right
                    content = normalize(chunk)  # treat raw text
                    
                    # Speak chunk immediately
                    piper.stdin.write((content + "\n").encode("utf8"))
                    piper.stdin.flush()
                    
                    #add text to end of console line
                    print(content, flush=True)
                    
                    #add token to full response
                    out += content
                    
        except Exception as e:
            print(f"\n[Stream Decode Error] {e}")
    print()
    return out



def normalize(text):
    replacements = {
        # Apostrophes / quotes (CRITICAL for Piper)
        "’": "'",
        "‘": "'",
        "‛": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "‟": '"',

        # Dashes (Piper pauses badly on long ones)
        "–": ", ",
        "—": ", ",
        "―": ", ",
        "−": "-",

        # Ellipsis (prevents long silence)
        "…": "...",

        # Spaces / invisible chars (can break synthesis)
        "\u00A0": " ",
        "\u200B": "",
        "\u200C": "",
        "\u200D": "",

        # Symbols Piper reads literally
        "©": " copyright ",
        "®": " registered ",
        "™": " trademark ",
        "§": " section ",

        # Math (spoken equivalents)
        "≤": " less than or equal to ",
        "≥": " greater than or equal to ",
        "≠": " not equal to ",
        "≈": " approximately ",
        "∞": " infinity ",

        # Bullets / formatting
        "•": "",
        "·": "",
        "‣": "",

        # Common troublemakers
        "|": " or ",
        "&": " and ",
        "@": " at ",
        "#": " number ",
        "%": " percent ",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Collapse repeated whitespace (helps rhythm)
    text = " ".join(text.split())

    return text



def readAudio():
    while True:
        data = piper.stdout.read(4096)
        audioQueue.put(data)

def playAudio():
    while True:
        chunk = audioQueue.get()
        sd_stream.write(chunk)

    
    
def checkQuit(userInput):
    quitWords=["exit", "quit", "close"]
    if userInput.strip().lower() in quitWords:
        print("WESTLEY: Goodbye.")
        return True
    return False

