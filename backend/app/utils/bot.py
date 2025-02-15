from app.models.appeal import Appeal


def send_new_appeal_message(appeal: Appeal) -> None:
    """
    Заглушка для отправки сообщения о новом обращении в бот

    Args:
        appeal: Обращение, о котором нужно уведомить
    """
    pass


def send_appeal_updated_message(appeal: Appeal) -> None:
    """
    Заглушка для отправки сообщения об обновлении обращения в бот

    Args:
        appeal: Обновленное обращение
    """
    pass
