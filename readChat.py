import pickle


def unpackList(l):
	
	for thing in l:
		if isinstance(thing, list): unpackList(thing)
		else: print(thing)


messages=pickle.load(open("chatHistory.pkl","rb"))

unpackList(messages)
