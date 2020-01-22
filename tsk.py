
import re
import os
import shutil
import string
import sqlite3


input_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/input/'
processed_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/processed/'
incorrect_input_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/incorrect_input/'
x = ''
for file in os.listdir(input_path):
    if file.endswith(".fb2"):
        x = file
        my_file = open(input_path + x, "r", encoding='utf-8')
        print("File name: ", my_file.name)
        text_string = my_file.read()

        book_name = re.findall(r'<book-title>(.*?)<\/book-title>', text_string, flags=re.DOTALL)
        print("Book name: ", book_name[-1])

        # only body text
        body = re.findall(r'<body>(.*?)<\/body>', text_string, flags=re.DOTALL)
        # print("Body: ", body)

        raw_text = ''.join(word for word in body)
        # print("Raw text: ", raw_text)

        # text without tags
        tags = re.compile('<.*?>')
        text = re.sub(tags, '', raw_text)
        # print(text)

        paragraphs = str(body).count('<p>')
        print("Number of paragraphs: ", paragraphs)

        punctuation = re.compile('[^\w\s\{P}-]')
        w_o_punctuation = re.sub(punctuation, '', text)
        # print(w_o_punct)

        no_dig_text = ''.join([word for word in w_o_punctuation if not word.isdigit()])
        # print(no_dig_text)

        # deleting words which starts with '-'
        norm_text = " ".join(filter(lambda x: x[0] != '-', no_dig_text.split()))
        # print(norm_text)

        # number of words
        numb_of_words = len(norm_text.split())
        print("Number of words: ", numb_of_words)

        # to find symbols that should be excluded
        # print(set(no_dig_text))

        # number of letters
        number_of_letters = 0
        for letter in norm_text:
            if letter != string.punctuation and letter != ' ' and letter != '\n' and letter != '\xa0' and letter != '-':
                number_of_letters += 1
        print("Number of letters in the text: ", number_of_letters)

        # words in lowercase and capital letters
        lower = 0
        capital = 0
        others = 0
        for line in norm_text.split():
            if line == line.lower():
                lower += 1
            elif line == line.capitalize():
                capital += 1
            else:
                others += 1
                # print(line)
        print("Number of words in lowercase: ", lower)
        print("Number of words with capital letter: ", capital)
        print("Number of other words: ", others)

        words_list = norm_text.split()
        words = {}
        for word in words_list:
            if word.capitalize() not in words and word.upper() not in words and word.lower() not in words:
                if word == word.upper():
                    words[word.capitalize()] = [1, 1]
                else:
                    words[word.capitalize()] = [1, 0]
            elif word.capitalize() in words or word.upper() in words or word.lower() in words:
                if word == word.upper():
                    words[word.capitalize()][0] += 1
                    words[word.capitalize()][1] += 1
                else:
                    words[word.capitalize()][0] += 1
        print("Frequency of words: ", words)

        book = book_name = book_name[-1]
        book_name = ''.join('_' if letter == " " else letter for letter in book_name)
        print(book_name)
        connection = sqlite3.connect('C:/Users/Vitaly_Gerasimovich/Desktop/Files/Database.db')
        cur = connection.cursor()
        # creating tables and inserting data in it
        cur.execute(
            "CREATE TABLE IF NOT EXISTS BOOKS(book_name text, number_of_paragraph INTEGER, number_of_words INTEGER, number_of_letters INTEGER, words_with_capital_letters INTEGER, words_in_lowercase INTEGER)")
        cur.execute("INSERT INTO BOOKS VALUES (?, ?, ?, ?, ?, ?)",
                    (book, paragraphs, numb_of_words, number_of_letters, capital, lower))
        connection.commit()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS {} (Word text, count INTEGER, count_uppercase INTEGER)".format(book_name))
        for k, v in words.items():
            cur.execute("INSERT INTO {} VALUES (?, ?, ?)".format(book_name), (k, v[0], v[1]))
        connection.commit()
        my_file.close()
        #move processed files into new folder
        shutil.move(input_path + file, processed_path + file)
    else:
        shutil.move(input_path + file, incorrect_input_path + file)



