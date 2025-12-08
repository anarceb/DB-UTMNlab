"""
Модуль работы с файловым хранилищем документов
"""

import os
import uuid
from werkzeug.utils import secure_filename
from database.db import execute_query  # Добавляем импорт
from config import allowed_file
import datetime
import traceback  

def get_upload_folder():
    """Возвращает путь к папке для загрузки файлов"""
    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    print(f"DEBUG: Upload folder path: {upload_folder}")
    os.makedirs(upload_folder, exist_ok=True)
    
    # Проверяем права доступа
    try:
        test_file = os.path.join(upload_folder, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print(f"DEBUG: Write permissions: OK")
    except Exception as e:
        print(f"DEBUG: Write permissions error: {e}")
    
    return upload_folder

def get_department_folder(department_id):
    """Возвращает путь к папке отдела"""
    upload_folder = get_upload_folder()
    department_folder = os.path.join(upload_folder, f'department_{department_id}')
    os.makedirs(department_folder, exist_ok=True)
    return department_folder

def get_public_folder():
    """Возвращает путь к папке публичных документов"""
    upload_folder = get_upload_folder()
    public_folder = os.path.join(upload_folder, 'public')
    os.makedirs(public_folder, exist_ok=True)
    return public_folder

def save_document_file(file, department_id, confidentiality_level, document_id=None, use_custom_name=None):
    """
    Сохраняет файл документа в соответствующую папку
    use_custom_name: если указано, использует это имя вместо оригинального
    """
    try:
        if file is None or not hasattr(file, 'filename') or not file.filename:
            return None, None, None
        
        try:
            if department_id is None:
                department_id = 1
            department_id = int(department_id)
            confidentiality_level = int(confidentiality_level)
        except (ValueError, TypeError):
            return None, None, None
        
        # ИСПРАВЛЕНО: Используем кастомное имя если указано, иначе оригинальное
        if use_custom_name:
            # Кастомное имя из формы
            original_filename = use_custom_name
            # Добавляем расширение если его нет
            if not os.path.splitext(original_filename)[1]:
                # Берем расширение из оригинального файла
                orig_ext = os.path.splitext(file.filename)[1]
                original_filename = f"{original_filename}{orig_ext}"
        else:
            # Оригинальное имя файла
            original_filename = file.filename
        
        # Безопасное имя файла
        safe_filename = secure_filename(original_filename)
        
        # Если после secure_filename имя стало пустым
        if not safe_filename or safe_filename == '':
            safe_filename = f"document_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Определяем расширение из безопасного имени
        file_extension = os.path.splitext(safe_filename)[1].lower()
        
        # Если нет расширения, определяем его
        if not file_extension:
            if hasattr(file, 'content_type'):
                mime_to_ext = {
                    'application/pdf': '.pdf',
                    'application/msword': '.doc',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                    'application/vnd.ms-excel': '.xls',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'text/plain': '.txt',
                }
                file_extension = mime_to_ext.get(file.content_type, '.bin')
            else:
                file_extension = '.bin'
            
            # Добавляем расширение к имени
            base_name = safe_filename
            safe_filename = f"{base_name}{file_extension}"
        else:
            # Уже есть расширение
            base_name = os.path.splitext(safe_filename)[0]
        
        # Определяем папку для сохранения
        if confidentiality_level == 0:
            relative_folder = 'public'
            save_folder = get_public_folder()
        else:
            relative_folder = f'department_{department_id}'
            save_folder = get_department_folder(department_id)
        
        # Генерируем окончательное имя файла
        filename = safe_filename
        
        # Проверяем существование и добавляем номер если нужно
        counter = 1
        while os.path.exists(os.path.join(save_folder, filename)):
            name_without_ext = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            # Убираем предыдущий номер если есть
            if '_' in name_without_ext and name_without_ext.split('_')[-1].isdigit():
                base = '_'.join(name_without_ext.split('_')[:-1])
            else:
                base = name_without_ext
            
            filename = f"{base}_{counter}{ext}"
            counter += 1
            if counter > 100:
                filename = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
                break
        
        # Если заменяем существующий документ
        if document_id:
            try:
                old_doc = execute_query(
                    "SELECT stored_file_path FROM documents WHERE document_id = %s",
                    (document_id,)
                )
                if old_doc and old_doc[0]['stored_file_path']:
                    delete_document_file(old_doc[0]['stored_file_path'])
            except Exception:
                pass
        
        # Сохраняем файл
        file_path = os.path.join(save_folder, filename)
        
        if hasattr(file, 'seek'):
            file.seek(0)
        
        file.save(file_path)
        
        if not os.path.exists(file_path):
            return None, None, None
        
        file_size = os.path.getsize(file_path)
        relative_path = f"{relative_folder}/{filename}"
        
        # ИСПРАВЛЕНО: Возвращаем оригинальное имя (то что видит пользователь) и имя файла на диске
        return relative_path, original_filename, file_size
        
    except Exception as e:
        print(f"ERROR in save_document_file: {e}")
        traceback.print_exc()
    
    return None, None, None

def generate_new_path(department_id, confidentiality_level, file_extension):
    """Генерирует новый путь для файла"""
    import uuid
    
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    
    if confidentiality_level == 0:
        return f"public/{unique_filename}"
    else:
        return f"department_{department_id}/{unique_filename}"

def get_document_file_path(stored_file_path):
    """
    Возвращает абсолютный путь к файлу документа
    """
    upload_folder = get_upload_folder()
    
    # Если путь уже правильный
    if stored_file_path.startswith(('public/', 'department_')):
        return os.path.join(upload_folder, stored_file_path)
    
    # Преобразуем старые пути
    path_mapping = {
        '/docs/public/rules_osago.pdf': 'public/rules_osago.pdf',
        '/docs/public/tariffs_2025.pdf': 'public/tariffs_2025.pdf',
        '/docs/sales/policy_001.pdf': 'department_2/policy_001.pdf',
        '/docs/sales/policy_002.pdf': 'department_2/policy_002.pdf',
        '/docs/confidential/fin_report.xlsx': 'department_1/fin_report.xlsx',
        '/docs/confidential/strategy.pdf': 'department_1/strategy.pdf',
        '/docs/confidential/sales_plan.xlsx': 'department_2/sales_plan.xlsx',
    }
    
    if stored_file_path in path_mapping:
        new_path = path_mapping[stored_file_path]
        return os.path.join(upload_folder, new_path)
    
    # По умолчанию
    return os.path.join(upload_folder, stored_file_path)

def delete_document_file(stored_file_path):  # ДОБАВЛЯЕМ ЭТУ ФУНКЦИЮ
    """
    Удаляет файл документа
    """
    try:
        file_path = get_document_file_path(stored_file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"Error deleting document file: {e}")
    
    return False

def find_document_file(file_name):
    """
    Ищет файл документа по имени во всех папках
    """
    upload_folder = get_upload_folder()
    possible_folders = ['public', 'department_1', 'department_2', 'department_3', 'department_4']
    
    # Пробуем разные варианты имени
    possible_names = [
        file_name,
        secure_filename(file_name),
        file_name.replace(' ', '_'),
    ]
    
    for folder in possible_folders:
        folder_path = os.path.join(upload_folder, folder)
        if os.path.exists(folder_path):
            for name in possible_names:
                file_path = os.path.join(folder_path, name)
                if os.path.exists(file_path):
                    return file_path
    
    return None

def document_file_exists(stored_file_path):
    """
    Проверяет существует ли файл документа
    
    Args:
        stored_file_path: путь из БД или относительный путь
    
    Returns:
        bool: True если файл существует
    """
    try:
        file_path = get_document_file_path(stored_file_path)
        return os.path.exists(file_path)
    except:
        return False
    


def update_document_safely(document_id, update_data):
    """
    Обновляет документ в БД без активации проблемного триггера
    
    Args:
        document_id: ID документа
        update_data: словарь с полями для обновления
    
    Returns:
        bool: True если успешно
    """
    try:
        # Если в update_data есть file_name, добавляем его как title
        if 'file_name' in update_data:
            update_data_with_title = update_data.copy()
            update_data_with_title['title'] = update_data['file_name']
        else:
            update_data_with_title = update_data
        
        # Формируем SET часть запроса
        set_parts = []
        values = []
        
        for key, value in update_data_with_title.items():
            set_parts.append(f"{key} = %s")
            values.append(value)
        
        values.append(document_id)
        
        query = f"UPDATE documents SET {', '.join(set_parts)} WHERE document_id = %s"
        
        print(f"DEBUG: Executing safe update query: {query}")
        print(f"DEBUG: With values: {values}")
        
        execute_query(query, values, fetch=False)
        return True
        
    except Exception as e:
        print(f"Error updating document safely: {e}")
        return False
    

def validate_uploaded_file(file):
    """
    Валидирует загруженный файл
    """
    if not file:
        return False, "Файл не предоставлен"
    
    if not hasattr(file, 'filename') or not file.filename:
        return False, "Имя файла отсутствует"
    
    if not allowed_file(file.filename):
        return False, "Недопустимый тип файла"
    
    # Проверяем, что файл не пустой
    try:
        file.seek(0, 2)  # Переходим в конец файла
        size = file.tell()  # Получаем размер
        file.seek(0)  # Возвращаемся в начало
        if size == 0:
            return False, "Файл пустой"
    except:
        pass
    
    return True, "OK"


def ensure_file_extension(file_name, file_path):
    """
    Гарантирует что у файла есть расширение
    """
    # Если у имени файла уже есть расширение
    if os.path.splitext(file_name)[1]:
        return file_name
    
    # Получаем расширение из файла
    file_ext = os.path.splitext(file_path)[1]
    if file_ext:
        return f"{file_name}{file_ext}"
    
    return file_name