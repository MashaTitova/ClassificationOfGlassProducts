from vkbottle.bot import Bot


def create_bot(token: str) -> Bot:
    bot = Bot(token=token)

    from vk_bot.handlers import (
        common, logs, train, analysis, hyperparams,
        load_model, olap, upload, predict, router,
    )

    print("Регистрирую хендлеры...")
    for module in [common, logs, train, analysis, hyperparams,
                   load_model, olap, upload, predict, router]:
        if hasattr(module, "register_handlers"):
            print(f"  ok: {module.__name__}")
            module.register_handlers(bot)
        else:
            print(f"  FAIL: {module.__name__} — нет register_handlers")

    return bot
