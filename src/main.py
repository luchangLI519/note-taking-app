import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.models.note import Note

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')
# Allow overriding the DB via DATABASE_URL (useful for Supabase/Postgres)
# Example DATABASE_URL: postgres://user:pass@db.host:5432/dbname
DATABASE_URL = os.getenv('DATABASE_URL')
# Flag that indicates whether we successfully connected to a remote DB.
USE_REMOTE_DB = False

if DATABASE_URL:
    print(f'INFO: DATABASE_URL is set (length: {len(DATABASE_URL)})')
    # Normalize 'postgres://' -> 'postgresql+psycopg2://'
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+psycopg2://', 1)
        print('INFO: Normalized postgres:// to postgresql+psycopg2://')

    # Try a quick test connection to avoid long startup hangs when the
    # remote DB (e.g. Supabase) is unreachable from this environment.
    try:
        from sqlalchemy import create_engine
        print('INFO: Attempting to connect to remote database...')
        # Use a short connect timeout so startup fails fast if network blocks
        test_engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})
        with test_engine.connect() as conn:
            # successful connection
            USE_REMOTE_DB = True
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
            print('SUCCESS: Connected to remote database (Supabase)')
    except Exception as e:
        print(f'WARNING: could not connect to DATABASE_URL, falling back to local SQLite. Error: {type(e).__name__}: {e}')
else:
    print('INFO: DATABASE_URL not set, using local SQLite')

if not USE_REMOTE_DB:
    # Only create local database directory if using SQLite
    # On serverless platforms (Vercel), use /tmp which is writable
    if os.environ.get('VERCEL'):
        # Vercel serverless environment
        DB_PATH = '/tmp/app.db'
        print('INFO: Running on Vercel, using /tmp/app.db for SQLite')
    else:
        # Local development
        ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        DB_PATH = os.path.join(ROOT_DIR, 'database', 'app.db')
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    print(f'INFO: Using SQLite at {DB_PATH}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
    # If using the SQLite file (i.e. we didn't connect to a remote DB), run
    # simple additive migrations to add new columns
    if not USE_REMOTE_DB:
        def ensure_note_columns(db_path):
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("PRAGMA table_info(note)")
                existing = [r[1] for r in cur.fetchall()]
                alters = []
                if 'tags' not in existing:
                    alters.append("ALTER TABLE note ADD COLUMN tags TEXT")
                if 'event_date' not in existing:
                    alters.append("ALTER TABLE note ADD COLUMN event_date TEXT")
                if 'event_time' not in existing:
                    alters.append("ALTER TABLE note ADD COLUMN event_time TEXT")
                if 'position' not in existing:
                    alters.append("ALTER TABLE note ADD COLUMN position INTEGER DEFAULT 0")
                for stmt in alters:
                    try:
                        cur.execute(stmt)
                        print(f"Applied migration: {stmt}")
                    except Exception as e:
                        print(f"Failed to apply migration {stmt}: {e}")
                conn.commit()
            finally:
                try:
                    conn.close()
                except:
                    pass

        ensure_note_columns(DB_PATH)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Local development server only
    # For production deployment (Vercel), the app object is imported directly
    app.run(host='0.0.0.0', port=5001, debug=True)
