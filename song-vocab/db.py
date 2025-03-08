import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict

class Database:
    def __init__(self, db_path: str = "lyrics_results.db"):
        self.db_path = db_path
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    lyrics TEXT NOT NULL,
                    vocabulary TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_result(self, query: str, lyrics: str, vocabulary: List[str]) -> str:
        # Save to database and export to JSON
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO queries (query, lyrics, vocabulary, timestamp) VALUES (?, ?, ?, ?)",
                (query, lyrics, ','.join(vocabulary), datetime.now())
            )
            result_id = cursor.lastrowid

        # Export to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = self.results_dir / f"lyrics_result_{timestamp}.json"
        
        result_data = {
            "id": result_id,
            "query": query,
            "lyrics": lyrics,
            "vocabulary": vocabulary,
            "timestamp": datetime.now().isoformat()
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        return str(json_file)

    def save_and_export_result(self, query: str, lyrics: str, vocabulary: List[str]) -> str:
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO queries (query, lyrics, vocabulary, timestamp) VALUES (?, ?, ?, ?)",
                (query, lyrics, ','.join(vocabulary), datetime.now())
            )
            result_id = cursor.lastrowid

        # Export to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = self.results_dir / f"lyrics_result_{timestamp}.json"
        
        result_data = {
            "id": result_id,
            "query": query,
            "lyrics": lyrics,
            "vocabulary": vocabulary,
            "timestamp": datetime.now().isoformat()
        }

        with open(export_file, 'w') as f:
            json.dump(result_data, f, indent=2)

        return str(export_file)

    def get_results(self, limit: int = 10) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM queries ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def export_to_json(self, output_dir: str = "exports") -> str:
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"lyrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(output_dir) / filename
        
        results = self.get_results(limit=None)  # Get all results
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return str(filepath)

    def export_to_csv(self, output_dir: str = "exports") -> str:
        Path(output_dir).mkdir(exist_ok=True)
        filename = f"lyrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = Path(output_dir) / filename
        
        results = self.get_results(limit=None)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'query', 'lyrics', 'vocabulary', 'timestamp'])
            writer.writeheader()
            writer.writerows(results)
        
        return str(filepath)