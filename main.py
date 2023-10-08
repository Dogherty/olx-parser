from tkinter import *
from tkinter import ttk
import parseolx
import openpyxl
import datetime

#Створення класу вспливаючих підказок
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        # Визначення положення для відображення підказки
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Створення вікна підказки
        self.tooltip = Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True) # Прибрати рамку вікна
        self.tooltip.wm_geometry(f"+{x}+{y}") # Задати геометрію віна

        label = ttk.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        # Приховати підказку
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Створення головного вікна додатку
root = Tk()
root.title('OLX parser')
root.geometry('800x600')
stored_contents = []
text = StringVar()

text1 = StringVar()
values = parseolx.start()
list_categories = ['Всі оголошення']
for i in values:
    list_categories.append(i)

paned_window = ttk.PanedWindow(root, orient=HORIZONTAL)
paned_window.pack(expand=True, fill=BOTH)
control_frame = ttk.Frame(paned_window, width=150)

# Створення віджетів і елементів інтерфейсу в головному вікні
lable_search = ttk.Label(control_frame, text='Що шукаємо?')
lable_search.pack(pady=10)

entry_search = ttk.Entry(control_frame, textvariable=text)
entry_search.pack()

lable_pages = ttk.Label(control_frame, text='Сортувати за:')
lable_pages.pack(pady=10)

combobox_sort = ttk.Combobox(control_frame, values=['Найдешевші', 'Найдорожчі', 'Найновіші', 'Рекомендоване вам'])
combobox_sort.set('Рекомендоване вам')
combobox_sort.pack()

lable_pages = ttk.Label(control_frame, text='Кількість сторінок (?):')
lable_pages.pack(pady=10)
tooltip = ToolTip(lable_pages, 'Залиште пустим, якщо потрібно продивитись всі сторінки')
entry_pages = ttk.Entry(control_frame, textvariable=text1)
entry_pages.pack()

button_find = ttk.Button(control_frame, text='Пошук', command=lambda: get_content(text.get(), text1.get(), combobox_categories.get(), combobox_sort.get()))
button_find.pack(pady=10)

combobox_categories = ttk.Combobox(control_frame, values=list_categories)
combobox_categories.set('Всі оголошення')
combobox_categories.pack(pady=10)

button_save_xlsx = ttk.Button(control_frame, text='Зберегти як Exel', command=lambda: save_as_xlxs())
button_save_xlsx.pack(pady=10)

paned_window.add(control_frame)

columns = ['text', 'price', 'url']
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('text', text='Текст')
tree.heading('price', text='Ціна')
tree.heading('url', text='Посилання')
tree.pack(expand=True, fill=BOTH)
paned_window.add(tree)

# Функція для откримання списку зі списків оголошень
def get_content(text, pages, categories, sort):
    global text1
    global tree
    global stored_contents
    contents = parseolx.parser(text, pages, categories, sort)
    tree.delete(*tree.get_children())
    for col in columns:
        tree.column(col, stretch=False)
    for content in contents:
        tree.insert("", END, values=content)
    stored_contents = contents

# Функція для збереження в Ексель-файл
def save_as_xlxs():
    global stored_contents
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet['A1'] = "Текст"
    sheet['B1'] = "Ціна"
    sheet['C1'] = "Посилання"
    index = 2
    for content in stored_contents:
        sheet[f'A{index}'] = content[0]
        sheet[f'B{index}'] = content[1]
        sheet[f'C{index}'] = content[2]
        index += 1
    time = str(datetime.datetime.now()).replace(':', '.')
    workbook.save(f'{text.get()} {time}.xlsx')

root.mainloop() # Запуск головного циклу додатка
