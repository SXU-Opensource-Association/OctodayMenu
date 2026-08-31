from alembic.config import Config

from app.core.alembic_config import set_database_url


def test_set_database_url_preserves_percent_encoded_password():
    database_url = "mysql+pymysql://user:encoded%21password@127.0.0.1:3306/app"
    config = Config()

    set_database_url(config, database_url)

    assert config.get_main_option("sqlalchemy.url") == database_url
