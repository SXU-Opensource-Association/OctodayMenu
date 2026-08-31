import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "SXUWhatEat")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.database_url = os.getenv(
            "DATABASE_URL",
            "mysql+pymysql://sxuwhateat:password@127.0.0.1:3306/sxuwhateat?charset=utf8mb4",
        )
        self.secret_key = os.getenv("SECRET_KEY", "change-me-in-local-env")
        if self.environment == "production" and (
            self.secret_key == "change-me-in-local-env" or len(self.secret_key) < 32
        ):
            raise RuntimeError("生产环境必须配置至少 32 位的 SECRET_KEY")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.auth_cookie_name = "sxuwhateat_auth"
        cookie_secure = os.getenv("AUTH_COOKIE_SECURE")
        self.auth_cookie_secure = (
            self.environment == "production"
            if cookie_secure is None
            else cookie_secure.strip().lower() == "true"
        )
        self.super_admin_email = os.getenv("SUPER_ADMIN_EMAIL")
        self.super_admin_password = os.getenv("SUPER_ADMIN_PASSWORD")
        self.smtp_host = os.getenv("SMTP_HOST")
        try:
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        except ValueError:
            self.smtp_port = None
        smtp_secure = os.getenv("SMTP_SECURE", "false").lower()
        self.smtp_secure = {"true": True, "false": False}.get(smtp_secure)
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.mail_from = os.getenv("MAIL_FROM")
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
            if origin.strip()
        ]


def get_settings() -> Settings:
    return Settings()
