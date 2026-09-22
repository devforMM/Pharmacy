from models.DataBase import session_maker

def get_session():
    session=session_maker()
    try: 
        yield session
    finally:
        session.close()