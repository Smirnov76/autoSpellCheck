import os.path
from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext, filedialog
from tkinter.messagebox import showinfo, showerror
import tkinter as tk
import site
import urllib.request
import shutil
import enchant
from enchant.checker import SpellChecker
import difflib

# author: Smirnov Alexander
# e-mail: asmirnov_1991@mail.ru

class App(tk.Tk):

    dictionary = enchant.Dict("ru_RU")
    checker = SpellChecker("ru_RU")
    error_correct = {}  # dictionary for pairs of error and correct words

    # function for highlight word
    def highlightWord(self, words, text, color, text_widget):
        for l, line in enumerate(text.split("\n")):
            for word in words:
                if word in line:
                    start_index = line.index(word)
                    end_index = start_index + len(word)
                    text_widget.tag_add("highlight", f"{l+1}.{start_index}", f"{l+1}.{end_index}")
        text_widget.tag_config("highlight", background=color)

    # function for replace selected word
    def replaceWord(self, old_word, new_word):
        text = self.output_text.get("1.0", END)
        if self.error_correct.get(old_word) is not None:
            replace_word = self.error_correct[old_word]
            right_text = text.replace(replace_word, new_word)
        else:
            right_text = text.replace(old_word, new_word)

        self.error_correct[old_word] = new_word

        self.output_text.delete("1.0", END)
        right_text = right_text.strip()
        self.output_text.insert("1.0", right_text)
        self.highlightWord(self.error_correct.values(), right_text, "green2", self.output_text)

    # function for select word in input textbox
    def selectionWord(self, event):
        try:
            word = self.input_text.selection_get()
            suggestions = set(self.dictionary.suggest(word))

            self.context_menu = tk.Menu(self.input_text, tearoff=0)
            for suggest_word in suggestions:
                self.context_menu.add_command(label=suggest_word, command=lambda sword=suggest_word:
                self.replaceWord(word, sword))
            self.context_menu.post(event.x_root, event.y_root)
        except Exception:
            pass

    # function for spelling correction text
    def spellingCorrection(self):
        text = self.input_text.get("1.0", END)
        right_text = text

        self.checker.set_text(text)
        similarity = {}

        for value in self.checker:
            suggestions = set(self.dictionary.suggest(value.word))
            for sugges_word in suggestions:
                measure = difflib.SequenceMatcher(None, value.word, sugges_word).ratio()
                similarity[measure] = sugges_word
            correct_word = similarity[max(similarity.keys())]
            right_text = right_text.replace(value.word, correct_word)
            self.error_correct[value.word] = correct_word
            similarity.clear()

        self.highlightWord(self.error_correct.keys(), text, "red", self.input_text)
        self.output_text.delete("1.0", END)
        right_text = right_text.strip()
        self.output_text.insert("1.0", right_text)
        self.highlightWord(self.error_correct.values(), right_text, "green2", self.output_text)

    # function for open and read text file
    def openFile(self):
        filepath = filedialog.askopenfilename(title="Открыть файл", initialdir=os.path.abspath(os.getcwd()),
                                              filetypes=[("text files", "*.txt")])
        if filepath != "":
            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()
                self.input_text.delete("1.0", END)
                self.input_text.insert("1.0", text)

    # function for save result text file
    def saveFile(self):
        filepath = filedialog.asksaveasfilename(title="Сохранить файл", initialfile='right_text.txt',
                                                initialdir=os.path.abspath(os.getcwd()),
                                                filetypes=[("text files", "*.txt")])

        if filepath != "":
            with open(filepath, "w", encoding="utf-8") as file:
                text = self.output_text.get("1.0", END)
                file.write(text)

    # function for view info about this program
    def openInfo(self):
        message = "Программа автоматической проверки орфографии текcта.\n\n" \
                  "Автор: Смирнов Александр Владимирович \n" \
                  "e-mail: asmirnov_1991@mail.ru\n\n" \
                  "Данное ПО было разработанно в качестве итогового проекта " \
                  "по программе повышения квалификации на языке Python\n\n" \
                  "2023 год"
        showinfo(title="Информация", message=message)

    # initialization GUI
    def __init__(self):
        super().__init__()
        # check and download dictionary files for russian language
        path_to_dict = os.path.join(site.getsitepackages()[1], "enchant\data\mingw64\share\enchant\hunspell")
        if not os.path.exists(os.path.join(path_to_dict, "ru_RU.aff")):
            urllib.request.urlretrieve("https://raw.githubusercontent.com/LibreOffice/dictionaries/master/ru_RU/ru_RU.aff",
                                       "ru_RU.aff")
            urllib.request.urlretrieve("https://raw.githubusercontent.com/LibreOffice/dictionaries/master/ru_RU/ru_RU.dic",
                                       "ru_RU.dic")
            shutil.copy2("ru_RU.aff", path_to_dict)
            shutil.copy2("ru_RU.dic", path_to_dict)

        # set main window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        main_win_size = f"{int(screen_width/3)+60}x{int(screen_height/3)+15}"

        self.title("SpellCheck")
        self.geometry(main_win_size)

        # main top menu
        self.menu = Menu()
        self.file_menu = Menu(tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.openFile)
        self.file_menu.add_command(label="Сохранить", command=self.saveFile)
        self.info_menu = Menu(tearoff=0)
        self.info_menu.add_command(label="О программе", command=self.openInfo)
        self.menu.add_cascade(label="Файл", menu=self.file_menu)
        self.menu.add_cascade(label="Информация", menu=self.info_menu)
        self.config(menu=self.menu)

        # frames, textboxes and button
        self.top_frame = ttk.LabelFrame(self, text="Исходный текст")
        self.middle_frame = Frame(self)
        self.bottom_frame = ttk.LabelFrame(self, text="Исправленный текст")

        self.input_text = scrolledtext.ScrolledText(self.top_frame, height=8, wrap=WORD, state=NORMAL)
        self.input_text.bind("<Button-3>", self.selectionWord)
        self.output_text = scrolledtext.ScrolledText(self.bottom_frame, height=8, wrap=WORD, state=NORMAL)

        self.check_spelling_btn = ttk.Button(self.middle_frame, text="Проверить орфографию", width=25,
                                         command=self.spellingCorrection)

        # pack all element of GUI on main window
        self.top_frame.pack(side=TOP, padx=5, fill=BOTH)
        self.middle_frame.pack(pady=5, fill=BOTH)
        self.bottom_frame.pack(side=TOP, padx=5, fill=BOTH)
        self.input_text.pack(side=TOP, expand=1, padx=8, pady=8, fill=BOTH)
        self.output_text.pack(side=TOP, expand=1, padx=8, pady=8, fill=BOTH)
        self.check_spelling_btn.pack()

# run this app
if __name__ == "__main__":
    app = App()
    app.mainloop()