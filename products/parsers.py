"""
Модуль для парсинга файлов с товарами (CSV, Excel)
"""
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation


class FileParser:
    """Базовый класс для парсинга файлов"""
    
    SUPPORTED_FORMATS = ['.csv', '.xlsx', '.xls']
    
    @staticmethod
    def detect_format(file_path: str) -> Optional[str]:
        """Определяет формат файла по расширению"""
        path = Path(file_path)
        ext = path.suffix.lower()
        if ext in FileParser.SUPPORTED_FORMATS:
            return ext
        return None
    
    @staticmethod
    def parse_csv(file_path: str, encoding: str = 'utf-8') -> List[Dict]:
        """
        Парсит CSV файл и возвращает список словарей
        
        Ожидаемые колонки:
        - store_name: название магазина (обязательно)
        - name: название товара (обязательно)
        - description: описание товара
        - sku: артикул
        - price: цена (обязательно)
        - stock_quantity: количество на складе
        - is_available: доступность (True/False или 1/0)
        """
        products = []
        try:
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                # Пробуем определить разделитель
                sample = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):  # Начинаем с 2, т.к. первая строка - заголовок
                    # Нормализуем ключи (убираем пробелы, приводим к нижнему регистру)
                    normalized_row = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}
                    products.append({
                        'row_number': row_num,
                        'data': normalized_row
                    })
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            for enc in ['cp1251', 'latin-1']:
                try:
                    return FileParser.parse_csv(file_path, encoding=enc)
                except:
                    continue
            raise ValueError(f"Не удалось определить кодировку файла {file_path}")
        except Exception as e:
            raise ValueError(f"Ошибка при чтении CSV файла {file_path}: {str(e)}")
        
        return products
    
    @staticmethod
    def parse_excel(file_path: str, sheet_name: Optional[str] = None) -> List[Dict]:
        """
        Парсит Excel файл и возвращает список словарей
        
        Ожидаемые колонки те же, что и для CSV
        """
        products = []
        try:
            # Читаем Excel файл
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Нормализуем названия колонок
            df.columns = df.columns.str.strip().str.lower()
            
            # Конвертируем в список словарей
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                # Заменяем NaN на пустые строки
                row_dict = {k: ('' if pd.isna(v) else str(v).strip()) for k, v in row_dict.items()}
                products.append({
                    'row_number': idx + 2,  # +2 потому что Excel нумеруется с 1 и есть заголовок
                    'data': row_dict
                })
        except Exception as e:
            raise ValueError(f"Ошибка при чтении Excel файла {file_path}: {str(e)}")
        
        return products
    
    @staticmethod
    def parse_file(file_path: str, **kwargs) -> List[Dict]:
        """
        Универсальный метод для парсинга файла любого поддерживаемого формата
        """
        file_format = FileParser.detect_format(file_path)
        
        if not file_format:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path}")
        
        if file_format == '.csv':
            return FileParser.parse_csv(file_path, **kwargs)
        elif file_format in ['.xlsx', '.xls']:
            return FileParser.parse_excel(file_path, **kwargs)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_format}")

