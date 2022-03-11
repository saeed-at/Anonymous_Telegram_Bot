from types import SimpleNamespace
from src.utils.keyboard import create_keyboard


keys = SimpleNamespace(
    random_connect = ':busts_in_silhouette: گفتگو ناشناس',
    settings = ':gear: تنظیمات',
    faal = ':open_book: فال',
    exit = ':cross_mark: خروج',
)

keyboards = SimpleNamespace(
    main = create_keyboard(keys.random_connect, keys.settings, keys.faal),
    discard = create_keyboard(keys.exit),
)
