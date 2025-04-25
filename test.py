import textdistance

word1 = "Анальгин"
word2 = "Аналгин"

similarity = textdistance.jaro_winkler(word1, word2)
print(f"Схожесть между '{word1}' и '{word2}': {similarity}")

