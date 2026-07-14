from pathlib import Path

from app.main import is_mutating_api, resolve_alembic_ini
from app.core.config import Settings


def test_resolve_alembic_ini_default():
    assert resolve_alembic_ini() == Path(__file__).resolve().parents[1] / 'alembic.ini'


def test_resolve_alembic_ini_env(monkeypatch, tmp_path):
    configured = tmp_path / 'alembic.ini'
    configured.write_text('[alembic]\n')
    monkeypatch.setenv('ALEMBIC_INI_PATH', str(configured))
    assert resolve_alembic_ini() == configured.resolve()


def test_health_live():
    from app.main import health_live
    assert health_live() == {'status': 'ok'}


def test_pool_and_tls_settings(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql+psycopg://u:p@example.com:5432/db?sslmode=require')
    monkeypatch.setenv('DB_POOL_SIZE', '4')
    settings = Settings()
    assert 'sslmode=require' in settings.database_url
    assert settings.db_pool_size == 4


def test_mutating_route_detection():
    assert is_mutating_api('POST', '/disaster-events')
    assert is_mutating_api('PATCH', '/ponds/1')
    assert not is_mutating_api('GET', '/disaster-events')
