import random
from sqlalchemy import func, select
from database import User, Word, UserWord

def get_or_create_user(session, telegram_id, username):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()

    if not user:
        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def add_word_to_user(session, user_id, word_text, translation):
    existing_word = session.query(Word).join(UserWord).filter(
        UserWord.user_id==user_id,
        Word.word==word_text,
        Word.translation==translation
    ).first()

    if existing_word:
        return existing_word

    new_word = Word(word=word_text.lower(), translation=translation.lower(), is_common=False)
    session.add(new_word)
    session.flush()

    user_word = UserWord(word_id=new_word.id, user_id=user_id)
    session.add(user_word)

    session.commit()
    session.refresh(new_word)
    return new_word

def get_random_word(session, user_id):
    common_words_subquery = session.query(Word.id).filter(Word.is_common == True)
    user_words_subquery = session.query(UserWord.word_id).filter(UserWord.user_id == user_id)
    all_words = common_words_subquery.union(user_words_subquery)

    random_word = session.query(Word).filter(Word.id.in_(all_words)).order_by(func.random()).first()
    return random_word

def generate_options(session, correct_word):
    other_words = session.query(Word).filter(Word.id != correct_word.id).order_by(func.random()).limit(3).all()
    options = [correct_word.translation]
    for word in other_words:
        options.append(word.translation)
    while len(options) < 4:
        options.append(correct_word.translation)
    random.shuffle(options)
    return options

def delete_word_from_user(session, user_id, word_text, translation):
    existing_word = session.query(Word).join(UserWord).filter(
        UserWord.user_id == user_id,
        Word.word == word_text,
        Word.translation == translation,
        Word.is_common == False
    ).first()

    if not existing_word:
        return existing_word

    session.query(UserWord).filter(UserWord.word_id==existing_word.id, UserWord.user_id==user_id).delete()

    if session.query(UserWord).filter(UserWord.word_id==existing_word.id).count() == 0:
        session.delete(existing_word)
    session.commit()
    return True