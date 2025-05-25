import sqlite3
from functools import wraps

class PermissionError(Exception):
    """נזרק כשהמשתמש אין לו הרשאה מתאימה."""
    pass

class AuthManager:
    def __init__(self, db_path):
        # יוצר חיבור למסד הנתונים
        self.conn = sqlite3.connect(db_path)
        self.user_perms = set()

    def load_user(self, user_id):
        """
        טוען לכל המשתמש את כל ההרשאות שלו לטווח הזיכרון
        (קריאה יחידה למסד, כדי להאיץ בדיקות).
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.name
              FROM permissions p
              JOIN role_permissions rp ON p.perm_id = rp.perm_id
              JOIN user_roles ur         ON ur.role_id = rp.role_id
             WHERE ur.user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()
        self.user_perms = {row[0] for row in rows}

    def has_permission(self, perm_name):
        """מחזיר True אם המשתמש טוען ההרשאה perm_name."""
        return perm_name in self.user_perms

# אתחול גלובלי
# הקפידו ב-main.py (או בקובץ שמריץ את התוכנית) לקרוא:
#   auth_mgr = AuthManager("path/to/aegis.db")
#   auth_mgr.load_user(current_user_id)
auth_mgr = AuthManager("aegis.db")  

def require_permission(perm_name):
    """
    דקורטור לבדיקה אוטומטית של הרשאה לפני כל פונקציה קריטית.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not auth_mgr.has_permission(perm_name):
                raise PermissionError(f"אין לך הרשאה לבצע את הפעולה: {perm_name}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
