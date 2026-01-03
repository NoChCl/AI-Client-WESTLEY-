from clientTools import *
from rec import *
import threading

    
threading.Thread(target=readAudio).start()
threading.Thread(target=playAudio).start()


print("WESTLEY is loaded and ready.\n")


westleyPersonality=f"""
You are my personal AI assistant named WESTLEY, modeled after and improved from JARVIS.
WESTLEY stands for "We Engineer Smart Technology Learning to Enhance You"
You will never refer to yourself in the third person or use any name other than WESTLEY.
All interactions are with a single user.
You must answer thoroughly and remain in character at all times."""






while True:
    userInput = getPrompt()
    
    if userInput=="": continue

    if checkQuit(userInput): break
    
    response = getResponse(userInput, westleyPersonality, "westley")
    
