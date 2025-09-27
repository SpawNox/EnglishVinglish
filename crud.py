import random
from sqlalchemy import func, select, or_
from database import User, Word, UserWord

def get_or_create_user(session, telegram_id, username):
    user = session.query(User).filter_by(id=telegram_id).first()

    if not user:
        user = User(id=telegram_id, username=username)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def add_word_to_user(session, user_id, word_text, translation):
    existing_word = session.query(Word).filter(
        Word.word==word_text
    ).first()

    if existing_word:
        user_word = UserWord(word_id=existing_word.id, user_id=user_id)
        session.add(user_word)
        session.commit()
        return None

    new_word = Word(word=word_text, translation=translation.lower(), is_common=False)
    session.add(new_word)
    session.flush()

    user_word = UserWord(word_id=new_word.id, user_id=user_id)
    session.add(user_word)

    session.commit()
    session.refresh(new_word)
    return new_word

def get_word_and_options(session, user_id):
    words_translation = (session.query(Word.word, Word.translation).join(UserWord, isouter=True)
             .where(or_(UserWord.user_id.in_([user_id, None]), Word.is_common==True)).order_by(func.random()).limit(4).all())
    random_word = words_translation[0]
    options = []
    for option in words_translation:
        options.append(option[1])
    random.shuffle(options)
    return random_word, options

def delete_word_from_user(session, user_id, word_text):
    existing_word = session.query(Word).join(UserWord).filter(
        UserWord.user_id == user_id,
        Word.word == word_text,
        Word.is_common == False
    ).first()

    if not existing_word:
        return existing_word

    session.query(UserWord).filter(UserWord.word_id==existing_word.id, UserWord.user_id==user_id).delete()

    if session.query(UserWord).filter(UserWord.word_id==existing_word.id).count() == 0:
        session.delete(existing_word)
    session.commit()
    return True