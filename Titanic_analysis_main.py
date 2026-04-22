import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class CSVSortApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Сортировщик - Pandas")
        self.root.geometry("1100x650")
        
        self.df = None
        self.file_path = None
        self.original_df = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="📂 Загрузить CSV", command=self.load_csv, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить CSV", command=self.save_csv, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Сбросить", command=self.reset_data, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="ℹ Информация", command=self.show_info, width=15).pack(side=tk.LEFT, padx=5)
        
        # Информация о файле
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(side=tk.RIGHT)
        
        self.file_label = ttk.Label(info_frame, text="❌ Файл не загружен", foreground="red")
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        self.row_label = ttk.Label(info_frame, text="")
        self.row_label.pack(side=tk.LEFT, padx=10)
        
        # Панель сортировки
        sort_panel = ttk.LabelFrame(main_frame, text="🔧 Параметры сортировки (Pandas)", padding="10")
        sort_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Выбор колонки
        ttk.Label(sort_panel, text="Колонка:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.column_var = tk.StringVar()
        self.column_combo = ttk.Combobox(sort_panel, textvariable=self.column_var, 
                                         state="readonly", width=25, font=("Arial", 10))
        self.column_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Порядок сортировки
        ttk.Label(sort_panel, text="Порядок:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.order_var = tk.StringVar(value="asc")
        ttk.Radiobutton(sort_panel, text="📈 По возрастанию", variable=self.order_var, 
                       value="asc").grid(row=0, column=3, padx=5)
        ttk.Radiobutton(sort_panel, text="📉 По убыванию", variable=self.order_var, 
                       value="desc").grid(row=0, column=4, padx=5)
        
        # Тип сортировки
        ttk.Label(sort_panel, text="Тип данных:").grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        self.sort_type_var = tk.StringVar(value="auto")
        sort_type_combo = ttk.Combobox(sort_panel, textvariable=self.sort_type_var,
                                       values=["auto (авто)", "числовая", "строковая", "дата"],
                                       state="readonly", width=15)
        sort_type_combo.grid(row=0, column=6, padx=5, pady=5)
        
        # Кнопка сортировки
        ttk.Button(sort_panel, text="✅ ПРИМЕНИТЬ СОРТИРОВКУ", 
                  command=self.sort_data, width=20).grid(row=0, column=7, padx=20, pady=5)
        
        # Дополнительные опции
        options_frame = ttk.Frame(sort_panel)
        options_frame.grid(row=1, column=0, columnspan=8, pady=5)
        
        self.ignore_case_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Игнорировать регистр (для строк)", 
                       variable=self.ignore_case_var).pack(side=tk.LEFT, padx=10)
        
        self.na_last_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Пустые значения в конец", 
                       variable=self.na_last_var).pack(side=tk.LEFT, padx=10)
        
        # Панель с таблицей
        table_frame = ttk.LabelFrame(main_frame, text="📊 Данные", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фрейм для таблицы и скроллов
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")
        
        self.tree = ttk.Treeview(tree_container, yscrollcommand=vsb.set, 
                                  xscrollcommand=hsb.set, selectmode="extended")
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Нижняя панель со статусом
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_bar = ttk.Label(bottom_frame, text="✅ Готов к работе", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(bottom_frame, textvariable=self.progress_var)
        self.progress_label.pack(side=tk.RIGHT, padx=10)
        
    def load_csv(self):
        """Загрузка CSV файла с поддержкой разных кодировок"""
        file_path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # Пробуем разные кодировки
            encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251', 'latin1', 'iso-8859-1']
            self.df = None
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(file_path, encoding=encoding)
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
                    
            if self.df is None:
                messagebox.showerror("Ошибка", "Не удалось прочитать файл. Проверьте кодировку.")
                return
                
            self.file_path = file_path
            self.original_df = self.df.copy()
            
            # Обновляем информацию
            file_name = os.path.basename(file_path)
            self.file_label.config(text=f"📄 {file_name}", foreground="green")
            self.row_label.config(text=f"📊 {len(self.df)} строк × {len(self.df.columns)} колонок")
            
            # Обновляем список колонок
            columns = list(self.df.columns)
            self.column_combo['values'] = columns
            if columns:
                self.column_combo.current(0)
            
            # Отображаем данные
            self.display_data()
            
            self.status_bar.config(text=f"✅ Загружен файл: {file_name}")
            self.progress_var.set(f"Загружено {len(self.df)} записей")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            self.status_bar.config(text="❌ Ошибка загрузки файла")
            
    def display_data(self):
        """Отображение данных в таблице Treeview"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if self.df is None or len(self.df) == 0:
            return
            
        # Настраиваем колонки
        columns = list(self.df.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Устанавливаем заголовки и ширину колонок
        for col in columns:
            self.tree.heading(col, text=col)
            
            # Вычисляем оптимальную ширину
            str_col = str(col)
            max_len = len(str_col) * 10
            
            if len(self.df) > 0:
                sample_values = self.df[col].dropna().astype(str).head(100)
                if len(sample_values) > 0:
                    col_max_len = sample_values.str.len().max() * 8
                    max_len = max(max_len, min(col_max_len, 300))
            
            self.tree.column(col, width=min(max_len, 250))
        
        # Добавляем данные (ограничиваем для производительности)
        display_limit = 10000
        display_df = self.df.head(display_limit)
        
        for idx, row in display_df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                if pd.isna(val):
                    values.append("")
                else:
                    values.append(str(val))
            self.tree.insert("", "end", values=values)
        
        if len(self.df) > display_limit:
            self.progress_var.set(f"Показано {display_limit} из {len(self.df)} строк")
        else:
            self.progress_var.set(f"Показано {len(self.df)} строк")
            
    def sort_data(self):
        """Сортировка данных с помощью pandas"""
        if self.df is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите CSV файл")
            return
            
        column = self.column_var.get()
        if not column:
            messagebox.showwarning("Предупреждение", "Выберите колонку для сортировки")
            return
            
        try:
            ascending = self.order_var.get() == "asc"
            sort_type = self.sort_type_var.get()
            ignore_case = self.ignore_case_var.get()
            na_position = 'last' if self.na_last_var.get() else 'first'
            
            self.status_bar.config(text="⏳ Сортировка данных...")
            self.root.update()
            
            # Создаем копию для сортировки
            df_sorted = self.df.copy()
            
            # Выбираем метод сортировки в зависимости от типа
            if sort_type == "числовая" or (sort_type == "auto (авто)" and 
                                           pd.api.types.is_numeric_dtype(df_sorted[column])):
                # Числовая сортировка
                df_sorted = df_sorted.sort_values(
                    by=column, 
                    ascending=ascending, 
                    na_position=na_position
                )
                
            elif sort_type == "дата":
                # Попытка преобразовать в дату
                try:
                    df_sorted[column] = pd.to_datetime(df_sorted[column], errors='coerce')
                    df_sorted = df_sorted.sort_values(
                        by=column, 
                        ascending=ascending, 
                        na_position=na_position
                    )
                except:
                    # Если не получилось, сортируем как строки
                    df_sorted = df_sorted.sort_values(
                        by=column, 
                        ascending=ascending, 
                        na_position=na_position,
                        key=lambda x: x.astype(str)
                    )
                    
            else:
                # Строковая сортировка
                if ignore_case:
                    df_sorted = df_sorted.sort_values(
                        by=column, 
                        ascending=ascending, 
                        na_position=na_position,
                        key=lambda x: x.astype(str).str.lower()
                    )
                else:
                    df_sorted = df_sorted.sort_values(
                        by=column, 
                        ascending=ascending, 
                        na_position=na_position,
                        key=lambda x: x.astype(str)
                    )
            
            # Обновляем данные
            self.df = df_sorted.reset_index(drop=True)
            
            # Обновляем отображение
            self.display_data()
            
            order_text = "возрастанию" if ascending else "убыванию"
            type_text = f"({sort_type})" if sort_type != "auto (авто)" else ""
            
            self.status_bar.config(text=f"✅ Данные отсортированы по колонке '{column}' по {order_text} {type_text}")
            self.progress_var.set(f"Сортировка завершена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить сортировку:\n{str(e)}")
            self.status_bar.config(text="❌ Ошибка сортировки")
            
    def reset_data(self):
        """Сброс к исходным данным"""
        if self.original_df is not None:
            self.df = self.original_df.copy()
            self.display_data()
            self.status_bar.config(text="🔄 Данные сброшены к исходному состоянию")
            self.progress_var.set("Сброс выполнен")
        else:
            messagebox.showinfo("Информация", "Нет данных для сброса")
            
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
            self.status_bar.config(text="⏳ Сохранение файла...")
            self.root.update()
            
            self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            self.status_bar.config(text=f"✅ Файл сохранен: {os.path.basename(file_path)}")
            self.progress_var.set("Сохранение завершено")
            messagebox.showinfo("Успех", f"Файл успешно сохранен!\n{os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            self.status_bar.config(text="❌ Ошибка сохранения")
            
    def show_info(self):
        """Показать информацию о данных"""
        if self.df is None:
            messagebox.showinfo("Информация", "Данные не загружены")
            return
            
        info_text = f"""
📊 ИНФОРМАЦИЯ О ДАННЫХ
{'='*40}

📁 Файл: {os.path.basename(self.file_path) if self.file_path else 'Не указан'}
📏 Размер: {len(self.df)} строк × {len(self.df.columns)} колонок

📋 Колонки:
{', '.join(self.df.columns.tolist())}

🔢 Типы данных:
"""
        for col in self.df.columns:
            dtype = self.df[col].dtype
            non_null = self.df[col].count()
            null_count = len(self.df) - non_null
            info_text += f"  • {col}: {dtype} (непустых: {non_null}, пустых: {null_count})\n"
            
        messagebox.showinfo("Информация о данных", info_text)

def main():
    root = tk.Tk()
    app = CSVSortApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()