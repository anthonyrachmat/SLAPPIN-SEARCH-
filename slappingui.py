from tkinter import *
from tkinter.scrolledtext import ScrolledText
import webbrowser
import Query
from PIL import Image, ImageTk
import tkinter

class slappinGUI:

    def __init__(self, book_keeping, inverted_index_json, inverted_bigram_index_json):

        self.query_handler = Query.Query(book_keeping, inverted_index_json, inverted_bigram_index_json)

        root = Tk()
        root.title("SLAPPIN SEARCH!")

        path = "slappers.jpg"
        img = ImageTk.PhotoImage(Image.open(path))
        self.pic = Label(root, image = img)
        self.pic.place(x = 30, y = 15)

        root.geometry("1050x500")
        self.label1=Label(root, text = "SLAP your query here: ", font = ("Comic Sans MS", 14, "bold"))
        self.label1.pack(side = LEFT)

        self.entry = Entry(root, width = 20)
        self.entry.pack(side = LEFT)

        self.button = Button(root, text = "SLAP!", command = self.search)
        self.button.pack(side = LEFT)
        self.q_results = ScrolledText(root)
        self.q_results.pack(side = RIGHT)

        root.mainloop()

    def search(self):
        query = self.entry.get()
        self.query_handler.handle_query(query)
        self.q_results.delete(1.0, END)
        
        if len(self.query_handler.results) == 0:
            self.q_results.insert('insert', 'OH SLAP! No slap results found.')
        else:
            for r in self.query_handler.results:
                self.q_results.insert('insert', str(r) + "\n")

        
