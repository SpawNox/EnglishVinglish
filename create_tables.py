from database import Base, Word
from db_session import engine, get_session


def create_tables():
    Base.metadata.create_all(engine)

def add_common_words():
    with get_session() as session:

        common_words = [
            {"word": "red", "translation": "красный"},
            {"word": "blue", "translation": "синий"},
            {"word": "green", "translation": "зеленый"},
            {"word": "I", "translation": "я"},
            {"word": "you", "translation": "ты"},
            {"word": "he", "translation": "он"},
            {"word": "she", "translation": "она"},
            {"word": "it", "translation": "оно"},
            {"word": "we", "translation": "мы"},
            {"word": "they", "translation": "они"}
        ]

        for word_data in common_words:
            existing_word = session.query(Word).filter_by(word=word_data['word'], translation=word_data['translation']).first()
            if not existing_word:
                new_word = Word(**word_data)
                session.add(new_word)
        session.commit()

if __name__ == "__main__":
    create_tables()
    add_common_words()
    print('База данных создана!')

