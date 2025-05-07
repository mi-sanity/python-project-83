from datetime import datetime


class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_all_urls(self):
        with self.conn.cursor as cur:
            cur.execute(
                """
                SELECT urls.id, urls.name, urls.created_at, url_checks.status_code 
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                ORDER BY urls.created_at DESC
                """
            )
            return cur.fetchall()

    def get_url_id(self, url_id):
        with self.conn.cursor as cur:
            cur.execute(
                "SELECT * FROM urls WHERE id = %s", [url_id]
            )
            return cur.fetchone()

    def save_url(self, normal_url):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at)" 
                "VALUES (%s, %s) RETURNING id",
                (normal_url, datetime.now().strftime("%Y-%m-%d"))
            )
            self.conn.commit()
            return cur.fetchone()["id"]

    def get_url_name(self, normal_url):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM urls WHERE name = %s", [normal_url]
            )
            return cur.fetchone()

    def get_url_checks(self, url_id):
        with self.conn.cursor as cur:
            cur.execute(
                """
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY created_at DESC
                """,
                [url_id]
            )
            return cur.fetchall()
