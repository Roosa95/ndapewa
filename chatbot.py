from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
from chatterbot.comparisons import SpacySimilarity
from chatterbot.response_selection import get_most_frequent_response

chatbot = ChatBot(
    'FCIBot',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.MathematicalEvaluation',
        'chatterbot.logic.BestMatch',
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'statement_comparison_function': SpacySimilarity,
            'response_selection_method': get_most_frequent_response,
            'default_response': 'I am sorry, but I do not understand. I am still learning.',
            'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///database.sqlite3'
    )

#Train Chatbot with Chatterbot English Corpus and Custom Library Corpus
#trainer_corpus = ChatterBotCorpusTrainer(chatbot)
#trainer_corpus.train("./data/")

#Train Chatbot with Greetings and Library dataset in raw text format
with open('raw/FCI.txt', "r", encoding="UTF-8") as training_library:
    t_l = training_library.read().splitlines()
with open('raw/greeting.txt', "r", encoding="UTF-8") as training_greet:
    t_g = training_greet.read().splitlines()
#Merge training datasets
training_data = t_g + t_l

trainer = ListTrainer(chatbot)
trainer.train(training_data)