import spacy

nlp = spacy.load("en_core_web_sm")

text = "Why can't they accomplish their specific interests by striking the specific company they work at okay we tell that they want they will have the same goal because we tell that the the problems within the industry is called is coherent right we tell that in an industry uh the problems that people are saving are facing is very similar as the example i've given you on on uh how does the railway workers they want to strike for a better a better uh a better working environment and a shorter shorter a better safety safety standards we tell that these are the things that are common for all industrial workers and these are the most important stuff as for individual companies if you have individual demands it's okay for you to have this choice to create a workforce company but that is not the major goal uh in the current status quo and that is not not the most emerg not the most urgent issues so back to the points of this uh efficiency improved efficiency in workforce we we we see that in two perspectives first and workers we tell that workers could argue for more rights because this is easier and more likely to get the rights with industrial union."

doc = nlp(text)
sentences = [sent.text.strip() for sent in doc.sents]

for s in sentences:
    print(f"[{len(s.split())} words] {s}")
