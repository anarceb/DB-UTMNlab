"""
Модуль контроля доступа к документам
Проверяет права пользователей на просмотр, редактирование и удаление документов
"""

from database.db import execute_query

def get_user_department(user_id):
    """Получает отдел пользователя по его ID"""
    try:
        result = execute_query(
            "SELECT department_id FROM employees WHERE employee_id = %s", 
            (user_id,)
        )
        if result:
            return result[0]['department_id']
        return None
    except Exception as e:
        print(f"Error getting user department: {e}")
        return None

def can_view_document(user_role, user_dept_id, user_id, document):
    """
    Проверяет может ли пользователь просматривать документ
    
    Args:
        user_role: роль пользователя
        user_dept_id: ID отдела пользователя
        user_id: ID пользователя
        document: словарь с данными документа из БД
    
    Returns:
        bool: True если доступ разрешен
    """
    
    # company_director видит всё
    if user_role == 'company_director':
        return True
    
    # db_admin видит всё
    if user_role == 'db_admin':
        return True
    
    # Публичные документы видны всем
    if document.get('confidentiality_level') == 0:
        return True
    
    # Сотрудник видит документы своего отдела (уровни 0,1) и свои документы
    if user_role == 'employee':
        return (document.get('created_in_department_id') == user_dept_id 
                and document.get('confidentiality_level') in [0, 1]
                or document.get('created_by_employee_id') == user_id)
    
    # Начальник отдела видит все документы своего отдела
    if user_role == 'department_manager':
        return document.get('created_in_department_id') == user_dept_id
    
    # HR видит документы своего отдела (уровни 0,1)
    if user_role == 'hr_manager':
        return (document.get('created_in_department_id') == user_dept_id 
                and document.get('confidentiality_level') in [0, 1])
    
    # Аудитор
    if user_role == 'auditor':
        # Аудитор из отдела безопасности видит все документы своего отдела
        if user_dept_id == 4:  # Отдел безопасности
            return document.get('created_in_department_id') == user_dept_id
        else:
            # Остальные аудиторы видят публичные и ДСП
            return document.get('confidentiality_level') in [0, 1]
    
    # Публичные пользователи
    if user_role == 'public_users':
        return document.get('confidentiality_level') == 0
    
    return False

def can_edit_document(user_role, user_dept_id, user_id, document_id):
    """
    Проверяет может ли пользователь редактировать документ
    """
    try:
        document = get_document_by_id(document_id)
        if not document:
            return False
        
        # ОСОБЫЙ СЛУЧАЙ: company_director и db_admin могут редактировать все
        if user_role in ['company_director', 'db_admin']:
            return True
        
        # Аудиторы могут редактировать документы отдела безопасности
        if user_role == 'auditor' and user_dept_id == 4:
            return document['created_in_department_id'] == 4
        
        # Начальник отдела может редактировать документы своего отдела
        if user_role == 'department_manager':
            return document['created_in_department_id'] == user_dept_id
        
        # HR может редактировать документы своего отдела
        if user_role == 'hr_manager':
            return document['created_in_department_id'] == user_dept_id
        
        return False
    except Exception as e:
        print(f"Error checking edit permission: {e}")
        return False

def can_delete_document(user_role, user_dept_id, user_id, document_id):
    """
    Проверяет может ли пользователь удалить документ
    """
    try:
        document = get_document_by_id(document_id)
        if not document:
            return False
        
        # ОСОБЫЙ СЛУЧАЙ: company_director и db_admin могут удалять все
        if user_role in ['company_director', 'db_admin']:
            return True
        
        # Аудиторы могут удалять документы отдела безопасности
        if user_role == 'auditor' and user_dept_id == 4:
            return document['created_in_department_id'] == 4
        
        # Начальник отдела может удалять документы своего отдела
        if user_role == 'department_manager':
            return document['created_in_department_id'] == user_dept_id
        
        return False
    except Exception as e:
        print(f"Error checking delete permission: {e}")
        return False

def get_documents_for_user(user_role, user_dept_id, user_id):
    """
    Возвращает документы доступные пользователю
    
    Args:
        user_role: роль пользователя
        user_dept_id: ID отдела пользователя (может быть None)
        user_id: ID пользователя
    
    Returns:
        list: список документов
    """
    try:
        # 1. ОСОБЫЙ СЛУЧАЙ: company_director видит ВСЕ документы
        if user_role == 'company_director':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                ORDER BY d.created_at DESC
            """
            return execute_query(query)
        
        # 2. ОСОБЫЙ СЛУЧАЙ: db_admin тоже видит все документы
        if user_role == 'db_admin':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                ORDER BY d.created_at DESC
            """
            return execute_query(query)
        
        # 3. ВСЕ ОСТАЛЬНЫЕ РОЛИ - СТАРАЯ РАБОЧАЯ ЛОГИКА:
        
        # Если user_dept_id не указан - возвращаем пустой список
        if not user_dept_id:
            return []
        
        if user_role == 'employee':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                WHERE (d.created_in_department_id = %s AND d.confidentiality_level < 2)
                OR d.confidentiality_level = 0
                ORDER BY d.created_at DESC
            """
            return execute_query(query, (user_dept_id,))
        
        elif user_role == 'department_manager':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                WHERE d.created_in_department_id = %s
                OR d.confidentiality_level = 0
                ORDER BY d.created_at DESC
            """
            return execute_query(query, (user_dept_id,))
        
        elif user_role == 'hr_manager':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                WHERE d.confidentiality_level = 0
                OR d.created_in_department_id = %s
                ORDER BY d.created_at DESC
            """
            return execute_query(query, (user_dept_id,))
        
        elif user_role == 'auditor':
            query = """
                SELECT d.*, 
                       dep.name as department_name,
                       emp.full_name as created_by_name
                FROM documents d
                LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
                LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
                WHERE d.confidentiality_level < 2
                ORDER BY d.created_at DESC
            """
            return execute_query(query)
        
        return []
        
    except Exception as e:
        print(f"Error getting documents for user: {e}")
        return []

def get_document_by_id(document_id):
    """
    Получает документ по ID
    
    Args:
        document_id: ID документа
    
    Returns:
        dict: данные документа или None если не найден
    """
    try:
        result = execute_query("""
            SELECT d.*, dep.name as department_name, emp.full_name as created_by_name
            FROM documents d
            LEFT JOIN departments dep ON d.created_in_department_id = dep.department_id
            LEFT JOIN employees emp ON d.created_by_employee_id = emp.employee_id
            WHERE d.document_id = %s
        """, (document_id,))
        
        return result[0] if result else None
    except Exception as e:
        print(f"Error getting document by ID: {e}")
        return None

def check_document_access(user_role, user_dept_id, user_id, document_id, action='view'):
    """
    Проверяет доступ пользователя к документу
    
    Args:
        user_role: роль пользователя
        user_dept_id: ID отдела пользователя
        user_id: ID пользователя
        document_id: ID документа
        action: действие ('view', 'edit', 'delete')
    
    Returns:
        tuple: (has_access, document_data)
    """
    try:
        # Получаем информацию о документе
        document = get_document_by_id(document_id)
        if not document:
            return False, None
        
        # 1. ОСОБЫЙ СЛУЧАЙ: company_director имеет доступ ко всему
        if user_role == 'company_director':
            return True, document
        
        # 2. ОСОБЫЙ СЛУЧАЙ: db_admin имеет доступ ко всему
        if user_role == 'db_admin':
            return True, document
        
        # 3. ВСЕ ОСТАЛЬНЫЕ - СТАРАЯ ЛОГИКА:
        
        # Для аудитора
        if user_role == 'auditor':
            if document['confidentiality_level'] < 2:
                return True, document
            else:
                return False, document
        
        # Для начальника отдела
        if user_role == 'department_manager':
            if (document['created_in_department_id'] == user_dept_id or 
                document['confidentiality_level'] == 0):
                return True, document
            else:
                return False, document
        
        # Для hr_manager
        if user_role == 'hr_manager':
            if (document['confidentiality_level'] == 0 or 
                document['created_in_department_id'] == user_dept_id):
                return True, document
            else:
                return False, document
        
        # Для обычного сотрудника
        if user_role == 'employee':
            if (document['created_in_department_id'] == user_dept_id and 
                document['confidentiality_level'] < 2) or \
               document['confidentiality_level'] == 0:
                return True, document
            else:
                return False, document
        
        return False, document
        
    except Exception as e:
        print(f"Error checking document access: {e}")
        return False, None