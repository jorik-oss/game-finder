from werkzeug.security import generate_password_hash
from db import get_db_connection

def init_db():
    conn = get_db_connection()
    
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS game_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            genre TEXT,
            tags TEXT,
            platform TEXT,
            release_year TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            user_id INTEGER,
            parent_reply_id INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES game_requests(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (parent_reply_id) REFERENCES replies(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            reply_to_message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (reply_to_message_id) REFERENCES chat_messages(id) ON DELETE SET NULL
        );
        
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            reply_id INTEGER,
            chat_message_id INTEGER,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (reply_id) REFERENCES replies(id) ON DELETE CASCADE,
            FOREIGN KEY (chat_message_id) REFERENCES chat_messages(id) ON DELETE CASCADE,
            UNIQUE (user_id, chat_message_id),
            UNIQUE (user_id, reply_id),
            CHECK (user_id != sender_id),
            CHECK (is_read IN (0, 1)),
            CHECK (
                (reply_id IS NOT NULL AND chat_message_id IS NULL)
                OR
                (reply_id IS NULL AND chat_message_id IS NOT NULL)
            )
        );
        
        CREATE INDEX IF NOT EXISTS idx_game_requests_user_id ON game_requests(user_id);
        CREATE INDEX IF NOT EXISTS idx_replies_request_id ON replies(request_id);
        CREATE INDEX IF NOT EXISTS idx_replies_user_id ON replies(user_id);
        CREATE INDEX IF NOT EXISTS idx_replies_parent_reply_id ON replies(parent_reply_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_reply_to_message_id ON chat_messages(reply_to_message_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_sender_id ON notifications(sender_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_reply_id ON notifications(reply_id);
        CREATE INDEX IF NOT EXISTS idx_notifications_chat_message_id ON notifications(chat_message_id);
    ''')
    conn.commit()
    conn.close()
    
    
def seed_db():
    conn = get_db_connection()

    if conn.execute("SELECT 1 FROM users WHERE username = 'clone_0'").fetchone():
        conn.close()
        return

    users = {}

    for i in range(10):
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (f"clone_{i}", f"clone{i}@gmail.com", generate_password_hash(f"password{i + 1}"))
        )
        users[f"clone_{i}"] = cursor.lastrowid

    requests_data = [
        (
            "Поиск игры с открытым миром",
            "Ищу игру с открытым миром, исследованием территорий, строительством и выживанием. Хочется чего-то с большим количеством возможностей и интересными механиками.",
            "Sandbox, Survival",
            "open-world, crafting, exploration",
            "PC, Mobile, Console",
            "2011",
            "clone_0"
        ),
        (
            "Метроидвания с интересным миром",
            "Ищу метроидванию с красивым нарисованным миром, сложными боссами, секретными локациями и постепенным открытием новых способностей.",
            "Metroidvania, Action",
            "2D, exploration, difficult, boss-fights",
            "PC, Console",
            "2017",
            "clone_3"
        ),
        (
            "Головоломки от первого лица",
            "Нужна головоломка от первого лица с необычными механиками, физическими задачами и интересным сюжетом. Что-нибудь похожее на Portal 2.",
            "Puzzle, Adventure",
            "first-person, physics, science-fiction",
            "PC, Console",
            None,
            "clone_6"
        )
    ]

    request_ids = []
    request_authors = []

    for title, description, genre, tags, platform, year, author in requests_data:
        cursor = conn.execute(
            """
            INSERT INTO game_requests (
                user_id, title, description, genre,
                tags, platform, release_year
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (users[author], title, description, genre, tags, platform, year)
        )

        request_ids.append(cursor.lastrowid)
        request_authors.append(author)

    replies_data = [
        (0, "clone_1", None, "Посмотри Vintage Story. Там тоже выживание, строительство и исследование мира. Правда, игра заметно сложнее."),
        (0, "clone_2", 0, "Поддерживаю. В Vintage Story интересная система развития технологий и довольно глубокое выживание."),
        (0, "clone_4", 0, "Ещё можно попробовать Terraria. Там много исследования, секретов и различных предметов."),
        (0, "clone_5", None, "А тебе больше интересны строительство и создание предметов или именно исследование неизвестных территорий?"),
        (0, "clone_0", 3, "В первую очередь исследование. Хочется находить необычные места и постепенно открывать возможности мира."),
        (0, "clone_7", 4, "Тогда попробуй No Man's Sky. Там можно исследовать огромное количество планет."),

        (1, "clone_2", None, "Попробуй Ori and the Blind Forest. Там очень красивая атмосфера и интересное исследование мира."),
        (1, "clone_3", 6, "Ori я уже проходил. Очень понравилась атмосфера, но хотелось бы найти что-то с более сложными боями."),
        (1, "clone_8", 6, "Тогда посмотри Ender Lilies. Она довольно атмосферная, с исследованием мира и непростыми противниками."),
        (1, "clone_9", None, "Blasphemous тоже стоит проверить. Там необычный визуальный стиль и сложные противники."),
        (1, "clone_3", 9, "Да, Blasphemous уже добавил в список. По описанию подходит под то, что я ищу."),
        (1, "clone_1", 10, "Ещё можешь обратить внимание на Blasphemous 2."),

        (2, "clone_4", None, "Попробуй The Talos Principle. Там много головоломок от первого лица и интересный сюжет."),
        (2, "clone_6", 12, "Спасибо! Судя по описанию, это именно то, что я ищу."),
        (2, "clone_5", None, "Есть ещё The Turing Test. Она тоже построена вокруг головоломок от первого лица."),
        (2, "clone_7", 14, "А в ней есть полноценный сюжет или основное внимание уделено только задачам?"),
        (2, "clone_5", 15, "Сюжет есть, он постепенно раскрывается по мере прохождения."),
        (2, "clone_8", 13, "Я тоже рекомендую The Talos Principle. Особенно первую часть.")
    ]

    reply_ids = []

    for request_index, username, parent_index, message in replies_data:
        parent_id = reply_ids[parent_index] if parent_index is not None else None

        cursor = conn.execute(
            """
            INSERT INTO replies (
                request_id, user_id, parent_reply_id, message
            )
            VALUES (?, ?, ?, ?)
            """,
            (request_ids[request_index], users[username], parent_id, message)
        )

        reply_ids.append(cursor.lastrowid)

    chat_data = [
        ("clone_0", "Кто-нибудь недавно находил интересную игру для исследования мира?", None),
        ("clone_1", "Я сейчас играю в No Man's Sky. Очень нравится исследовать разные планеты.", 0),
        ("clone_2", "А мне больше нравятся метроидвании. Недавно снова начал проходить Hollow Knight.", 0),
        ("clone_3", "Кто-нибудь проходил Hollow Knight? Как вам дополнения?", None),
        ("clone_8", "Да, отличная игра. Особенно понравились боссы и скрытые локации.", 3),
        ("clone_9", "Я пока только начал проходить. Управление немного непривычное.", 3),
        ("clone_5", "Посоветуйте хорошие головоломки от первого лица.", None),
        ("clone_6", "Попробуй The Talos Principle, @clone_5. Думаю, тебе понравится.", 6),
        ("clone_4", "Portal 2 тоже отличный вариант. Там интересные механики и кооператив.", 6),
        ("clone_7", "Кто-нибудь знает хорошие игры на выживание?", None),
        ("clone_0", "Можно попробовать Vintage Story. Она довольно глубокая в плане выживания.", 9),
        ("clone_1", "Или Terraria, если нравится исследование и поиск предметов.", 9),
        ("clone_2", "Кто сегодня играет во что-нибудь интересное?", None),
        ("clone_3", "Я прохожу Ender Lilies. Атмосфера действительно хорошая.", 12),
        ("clone_8", "Как тебе игра, @clone_3? Сложные боссы?", 13),
        ("clone_9", "Я тоже хотел попробовать Ender Lilies. Стоит начинать?", 13),
        ("clone_5", "Нашёл интересную головоломку, называется The Turing Test.", None),
        ("clone_6", "Слышал о ней, но ещё не играл.", 16),
        ("clone_4", "Сегодня посмотрю несколько игр из рекомендаций. Спасибо всем!", None),
        ("clone_7", "Если найдёшь что-то интересное, напиши сюда, @clone_4.", 18)
    ]

    chat_ids = []

    for username, message, reply_index in chat_data:
        reply_to_id = chat_ids[reply_index] if reply_index is not None else None

        cursor = conn.execute(
            """
            INSERT INTO chat_messages (
                user_id, message, reply_to_message_id
            )
            VALUES (?, ?, ?)
            """,
            (users[username], message, reply_to_id)
        )

        chat_ids.append(cursor.lastrowid)

    reply_notifications = [
        (0, "clone_0"),
        (1, "clone_0"),
        (1, "clone_1"),
        (2, "clone_0"),
        (2, "clone_1"),
        (3, "clone_0"),
        (4, "clone_5"),
        (5, "clone_0"),
        (6, "clone_3"),
        (7, "clone_2"),
        (8, "clone_3"),
        (8, "clone_2"),
        (9, "clone_3"),
        (10, "clone_9"),
        (11, "clone_3"),
        (12, "clone_6"),
        (13, "clone_4"),
        (14, "clone_6"),
        (15, "clone_6"),
        (15, "clone_5"),
        (16, "clone_6"),
        (16, "clone_7"),
        (17, "clone_6")
    ]

    for reply_index, recipient in reply_notifications:
        sender = replies_data[reply_index][1]
    conn.execute(
            """
            INSERT INTO notifications (
                user_id, sender_id, reply_id, message
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                users[recipient],
                users[sender],
                reply_ids[reply_index],
                replies_data[reply_index][3]
            )
        )

    chat_notifications = [
        (1, "clone_0"),
        (2, "clone_0"),
        (4, "clone_3"),
        (5, "clone_3"),
        (7, "clone_5"),
        (8, "clone_5"),
        (10, "clone_7"),
        (11, "clone_7"),
        (14, "clone_3"),
        (15, "clone_3"),
        (17, "clone_5"),
        (19, "clone_4")
    ]

    for message_index, recipient in chat_notifications:
        sender = chat_data[message_index][0]

        conn.execute(
            """
            INSERT INTO notifications (
                user_id, sender_id, chat_message_id, message
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                users[recipient],
                users[sender],
                chat_ids[message_index],
                chat_data[message_index][1]
            )
        )

    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    init_db()
    seed_db()