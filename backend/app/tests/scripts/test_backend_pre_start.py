from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.backend_pre_start import init, logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    # Настраиваем поддержку контекстного менеджера
    session_mock.__enter__.return_value = session_mock
    session_mock.exec.return_value = MagicMock()

    with (
        patch("app.backend_pre_start.Session", return_value=session_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        assert session_mock.exec.call_count == 1, "exec should be called exactly once"
        call_args = session_mock.exec.call_args[0][0]
        assert isinstance(
            call_args, type(select(1))
        ), "exec should be called with a SELECT statement"
