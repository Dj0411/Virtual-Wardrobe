from config import app, mysql

def test_connection():
    with app.app_context():  # 🔹 Add this to create an application context
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT DATABASE();")
            db_name = cur.fetchone()
            print(f"✅ Successfully connected to database: {db_name}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_connection()
