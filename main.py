import re
import os
import shutil
import string
import sqlite3

input_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/input/'
processed_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/processed/'
incorrect_input_path = 'C:/Users/Vitaly_Gerasimovich/Desktop/Files/incorrect_input/'
connection = sqlite3.connect('C:/Users/Vitaly_Gerasimovich/Desktop/Files/Database.db')

class SQLwriter_fb2:
    def __init__(self, connection):
        self.connection = connection

    def create_populate_tables(self, book_name, paragraphs, words_number, letters, low_up_words, words):
        book = ''.join('_' if letter == " " else letter for letter in book_name)
        cur = self.connection.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS BOOKS(book_name text, number_of_paragraph INTEGER, number_of_words INTEGER, number_of_letters INTEGER, words_with_capital_letters INTEGER, words_in_lowercase INTEGER)")
        cur.execute("INSERT INTO BOOKS VALUES (?, ?, ?, ?, ?, ?)", (book, paragraphs, words_number, letters, low_up_words[1], low_up_words[0]))
        self.connection.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS {} (Word text, count INTEGER, count_uppercase INTEGER)".format(book))
        for k, v in words.items():
            cur.execute("INSERT INTO {} VALUES (?, ?, ?)".format(book), (k, v[0], v[1]))
        connection.commit()

class SQLwriter_another_file:
    def __init__(self):
        pass

class Parser_fb2:
    def __init__(self):
        pass

    def find_book_name(self, text_string):
            book_name = re.findall(r'<book-title>(.*?)<\/book-title>', text_string, flags=re.DOTALL)
            # print("Book name: ", book_name[-1])
            return book_name[-1]

    def find_body(self, text_string):
            body = re.findall(r'<body>(.*?)<\/body>', text_string, flags=re.DOTALL)
            raw_text = ''.join(word for word in body)
            return raw_text

    def count_paragraphs(self, raw_text):
            paragraphs = raw_text.count('<p>')
            return paragraphs

    def remove_tags(self, raw_text):
            raw_text = ''.join(word for word in raw_text)
            tags = re.compile('<.*?>')
            text = re.sub(tags, '', raw_text)
            return text

    def remove_punctuation(self, text):
            punctuation = re.compile('[^\w\s\{P}-]')
            w_o_punctuation = re.sub(punctuation, '', text)
            return w_o_punctuation

    def remove_digits(self, w_o_punctuation):
            no_dig_text = ''.join([word for word in w_o_punctuation if not word.isdigit()])
            return no_dig_text

    def remove_digit_rest(self, no_dig_text):
            norm_text = " ".join(filter(lambda x: x[0] != '-', no_dig_text.split()))
            return norm_text

    def count_letters(self, no_dig_text):
            number_of_letters = 0
            for letter in no_dig_text:
                if letter != string.punctuation and letter != ' ' and letter != '\n' and letter != '\xa0' and letter != '-':
                    number_of_letters += 1
            return number_of_letters

    def count_words(self, norm_text):
            numb_of_words = len(norm_text.split())
            return numb_of_words

    def count_low_up_words(self, norm_text):
            lower = 0
            capital = 0
            others = []
            for line in norm_text.split():
                if line == line.lower():
                    lower += 1
                elif line == line.capitalize():
                    capital += 1
                else:
                    others.append(line)
            return lower, capital

    def words_frequency(self, norm_text):
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
            return words

class Parser_another_file:
    def __init__(self):
        pass

class File:
    def __init__(self, input_path, processed_path, incorrect_input_path):
        self.input_path = input_path
        self.processed_path = processed_path
        self.incorrect_input_path = incorrect_input_path

    def checking(self):
        for file in os.listdir(self.input_path):
            if file.endswith(".fb2"):
                #continue
                File.open_f(self, file)
                # move processed files into new folder
                #shutil.move(input_path + file, processed_path + file)
            else:
                File.move_incorrect(self, file)
        return os.listdir(input_path)[0]

    def open_f(self, file):
        my_file = open(input_path + file, "r", encoding='utf-8')
        #print("File name: ", my_file.name)
        text_string = my_file.read()
        my_file.close()
        return text_string


    def move_processed(self, file):
        shutil.move(self.input_path + file, self.processed_path + file)

    def move_incorrect(self, file):
        shutil.move(self.input_path + file, self.incorrect_input_path + file)

class Logger:
    def __init__(self):
        pass

    def write_stat(self, file, book_name, paragraphs, words_number, letters):
        f = open(processed_path + "logger.txt", "a")
        f.write("\nFile: "+file+"\nBook name: "+book_name+"\nNumber of paragraphs: "+str(paragraphs))
        f.write("\nNumber of words: "+str(words_number)+"\nNumber of letters: "+str(letters)+'\n')
        f.close()

def main():
    f = File(input_path, processed_path, incorrect_input_path)
    file = f.checking()
    #print(file)
    stuffing = f.open_f(file)
    #print(stuffing)
    if file.endswith(".fb2"):
        p = Parser_fb2()
        book_name = p.find_book_name(stuffing)
        body = p.find_body(stuffing)
        paragraphs = p.count_paragraphs(body)
        text = p.remove_tags(body)
        punct = p.remove_punctuation(text)
        text_without_digits = p.remove_digits(punct)
        clean_text = p.remove_digit_rest(text_without_digits)
        letters = p.count_letters(text_without_digits)
        words_number = p.count_words(clean_text)
        low_up_words = p.count_low_up_words(clean_text)
        words = p.words_frequency(clean_text)
        s = SQLwriter_fb2(connection)
        s.create_populate_tables(book_name, paragraphs, words_number, letters, low_up_words, words)
        l = Logger()
        l.write_stat(file, book_name, paragraphs, words_number, letters)
        f.move_processed(file)
    else:
        pass

if __name__ == '__main__':
    main()
else:
    print('беда')


