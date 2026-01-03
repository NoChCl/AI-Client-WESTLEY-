import platform, queue, sounddevice, numpy, whisper
from scipy.io.wavfile import write

audioQueue = queue.Queue()



#Get OS, and import needed dependancys
osName = platform.system().lower()

if osName == "windows":
    import keyboard
elif osName == "linux":
    from gpiozero import Button
    RECORD_PIN = 17  # GPIO pin number
    recordButton = Button(RECORD_PIN, pull_up=True)
#Ensure OS is either Windows or Linux, dont know what to do with others rn
else:
    raise RuntimeError("Unsupported OS for record trigger")


model = whisper.load_model("base")

def whisperTranscribe(path):
    result = model.transcribe(path)
    return result["text"].strip()

def waitForRecordStart():
    """Blocks until recording should start"""
    if osName == "windows":
        print("Hold SPACE to record")
        keyboard.wait("space")

    elif osName == "linux":
        print("Waiting for GPIO button press")
        recordButton.wait_for_press()


def recordButtonOn():
    #Returns button state
    if osName == "windows":
        return keyboard.is_pressed("space")

    elif osName == "linux":
        return recordButton.is_pressed


def callback(indata, frames, time, status):
    audioQueue.put(indata.copy())


def getPrompt():
    
    while not audioQueue.empty():
        audioQueue.get()
    
    waitForRecordStart()
    
    audioFrames=[]
    
    
    stream = sounddevice.InputStream(
        samplerate=16000,
        channels=1,
        dtype="float32",
        callback=callback
    )
    
    
    with stream:
        while recordButtonOn():
            try:
                audioFrames += [audioQueue.get(timeout=0.1)]
            except queue.Empty:
                pass
    if not audioFrames:
        return ""
        
    audio = numpy.concatenate(audioFrames, axis=0)
    write("currPrompt.wav", 16000, audio)
    prompt=whisperTranscribe("currPrompt.wav")
    print(prompt)
    return prompt
