import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import os
import sqlite3
import jwt  # PyJWT library for JWT decoding

JWT_SECRET = os.environ.get("JWT_SECRET")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")

def verify_user_jwt(token: str) -> Optional[str]:
    """
    Verifies the JWT and returns the user_id if valid, else None.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_id")
    except Exception:
        return None

class Message:
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

class ConversationSession:
    def __init__(
        self,
        user_id: str,
        document_id: str,
        session_id: Optional[str] = None,
        parent_session_id: Optional[str] = None,
        user_token: Optional[str] = None
    ):
        if not user_token:
            raise PermissionError("Missing authentication token.")
        token_user_id = verify_user_jwt(user_token)
        if not token_user_id or str(token_user_id) != str(user_id):
            raise PermissionError("Authentication failed for user_id: {}".format(user_id))
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.document_id = document_id
        self.parent_session_id = parent_session_id  # For branching
        self.history: List[Message] = []
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = self.created_at
        self.summary: Optional[str] = None  # For context compression

    def add_message(self, role: str, content: str):
        msg = Message(role, content)
        self.history.append(msg)
        self.updated_at = msg.timestamp

    def get_history(self, window: int = 5) -> List[Dict[str, Any]]:
        # Sliding window: return last N messages
        return [m.to_dict() for m in self.history[-window:]]

    def summarize(self, summarizer_fn=None, max_tokens: int = 512):
        """
        Summarize conversation history for context compression.
        summarizer_fn: callable that takes a list of messages and returns a summary string.
        """
        if summarizer_fn:
            self.summary = summarizer_fn([m.content for m in self.history], max_tokens=max_tokens)
        else:
            # Simple fallback: join last N messages
            self.summary = "\n".join(m.content for m in self.history[-max_tokens:])
        return self.summary

    def branch(self) -> 'ConversationSession':
        """Create a new session branched from this one."""
        return ConversationSession(
            user_id=self.user_id,
            document_id=self.document_id,
            parent_session_id=self.session_id
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "parent_session_id": self.parent_session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "history": [m.to_dict() for m in self.history],
            "summary": self.summary
        }

    @staticmethod
    def _get_db_path():
        # Use a central db directory for all .db files
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        db_dir = os.path.join(backend_dir, 'db')
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, 'conversations.db')

    @staticmethod
    def _init_db():
        db_path = ConversationSession._get_db_path()
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                document_id TEXT,
                parent_session_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                summary TEXT
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )''')
            conn.commit()

    def save(self, user_token: Optional[str] = None):
        if not user_token:
            raise PermissionError("Missing authentication token.")
        token_user_id = verify_user_jwt(user_token)
        if not token_user_id or str(token_user_id) != str(self.user_id):
            raise PermissionError("Authentication failed for user_id: {}".format(self.user_id))
        self._init_db()
        db_path = self._get_db_path()
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            # Upsert session
            c.execute('''INSERT OR REPLACE INTO sessions (session_id, user_id, document_id, parent_session_id, created_at, updated_at, summary)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (self.session_id, self.user_id, self.document_id, self.parent_session_id, self.created_at.isoformat(), self.updated_at.isoformat(), self.summary))
            # Delete old messages for this session
            c.execute('DELETE FROM messages WHERE session_id = ?', (self.session_id,))
            # Insert messages
            for m in self.history:
                c.execute('''INSERT INTO messages (session_id, role, content, timestamp)
                             VALUES (?, ?, ?, ?)''',
                          (self.session_id, m.role, m.content, m.timestamp.isoformat()))
            conn.commit()

    @staticmethod
    def load(session_id: str, user_token: Optional[str] = None) -> Optional['ConversationSession']:
        if not user_token:
            raise PermissionError("Missing authentication token.")
        token_user_id = verify_user_jwt(user_token)
        if not token_user_id:
            raise PermissionError("Invalid authentication token.")
        ConversationSession._init_db()
        db_path = ConversationSession._get_db_path()
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT session_id, user_id, document_id, parent_session_id, created_at, updated_at, summary FROM sessions WHERE session_id = ?', (session_id,))
            row = c.fetchone()
            db_user_id = row[1] if row else None
            if not row:
                return None
            # Always compare as strings
            if str(db_user_id) != str(token_user_id):
                raise PermissionError(f"User {token_user_id} not authorized for session {session_id}")
            session = ConversationSession(
                user_id=row[1],
                document_id=row[2],
                session_id=row[0],
                parent_session_id=row[3],
                user_token=user_token
            )
            session.created_at = datetime.fromisoformat(row[4])
            session.updated_at = datetime.fromisoformat(row[5])
            session.summary = row[6]
            # Load messages
            c.execute('SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id ASC', (session_id,))
            session.history = [Message(role, content, datetime.fromisoformat(ts)) for role, content, ts in c.fetchall()]
            return session
