import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class CSVSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сортировщик CSV файлов")
        self.root.geometry("900x600")
        
        self.df = None
        self.file_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="Загрузить CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Сохранить отсортированный CSV", command=self.save_csv).pack(side=tk.LEFT, padx=5)
        
        # Информация о файле
        self.file_label = ttk.Label(top_frame, text="Файл не загружен")
        self.file_label.pack(side=tk.LEFT, padx=20)
        
        # Панель сортировки
        sort_frame = ttk.LabelFrame(self.root, text="Параметры сортировки", padding="10")
        sort_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Выбор колонки для сортировки
        ttk.Label(sort_frame, text="Колонка для сортировки:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(sort_frame, textvariable=self.column_var, state="readonly", width=30)
        self.column_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Порядок сортировки
        ttk.Label(sort_frame, text="Порядок сортировки:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.order_var = tk.StringVar(value="asc")
        ttk.Radiobutton(sort_frame, text="По возрастанию", variable=self.order_var, value="asc").grid(row=0, column=3, padx=5)
        ttk.Radiobutton(sort_frame, text="По убыванию", variable=self.order_var, value="desc").grid(row=0, column=4, padx=5)
        
        # Кнопка сортировки
        ttk.Button(sort_frame, text="Применить сортировку", command=self.sort_data).grid(row=0, column=5, padx=20, pady=5)
        
        # область с таблицей
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Скроллы для таблицы
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Таблица для отображения данных
        self.tree = ttk.Treeview(tree_frame, 
                                 yscrollcommand=vsb.set, 
                                 xscrollcommand=hsb.set,
                                 selectmode="extended")
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Размещение таблицы и скроллов
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        
        self.status_bar = ttk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_csv(self):
        """Загрузка CSV файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Кодировки
            encodings = ['utf-8', 'cp1251', 'windows-1251', 'latin1']
            self.df = None
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                    
            if self.df is None:
                messagebox.showerror("Ошибка", "Не удалось прочитать файл. Проверьте кодировку.")
                return
                
            self.file_path = file_path
            self.file_label.config(text=f"Файл: {os.path.basename(file_path)}")
            
            # Обновляем список колонок
            self.column_combo['values'] = list(self.df.columns)
            if len(self.df.columns) > 0:
                self.column_combo.current(0)
            
            # Отображаем данные
            self.display_data()
            
            self.status_bar.config(text=f"Загружено {len(self.df)} строк, {len(self.df.columns)} колонок")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
            
    def display_data(self):
        """Отображение данных в таблице"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Настройка колонок
        self.tree['columns'] = list(self.df.columns)
        self.tree['show'] = 'headings'
        
        # Устанавливаем заголовки
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            # Определяем ширину колонки
            max_width = max(
                len(str(col)) * 10,
                self.df[col].astype(str).str.len().max() * 8
            )
            self.tree.column(col, width=min(max_width, 300))
        
        # Добавляем данные
        for idx, row in self.df.iterrows():
            values = [str(row[col]) if pd.notna(row[col]) else "" for col in self.df.columns]
            self.tree.insert("", "end", values=values)
            
    def sort_data(self):
        """Сортировка данных"""
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите CSV файл")
            return
            
        column = self.column_var.get()
        if not column:
            messagebox.showwarning("Предупреждение", "Выберите колонку для сортировки")
            return
            
        try:
            ascending = self.order_var.get() == "asc"
            
            # Сортировка с помощью pandas
            self.df = self.df.sort_values(by=column, ascending=ascending)
            
            # Обновляем отображение
            self.display_data()
            
            order_text = "возрастанию" if ascending else "убыванию"
            self.status_bar.config(text=f"Данные отсортированы по колонке '{column}' по {order_text}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить сортировку: {str(e)}")
            
    def save_csv(self):
        """Сохранение отсортированных данных в CSV"""
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Нет данных для сохранения")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Сохранить CSV файл",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Сохраняем с UTF-8 для лучшей совместимости с Excel
            self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
            self.status_bar.config(text=f"Файл сохранен: {os.path.basename(file_path)}")
            messagebox.showinfo("Успех", "Файл успешно сохранен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

def main():
    root = tk.Tk()
    app = CSVSortApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()