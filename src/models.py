from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    # is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorites: Mapped[list["Favorite"]] = relationship('Favorite', back_populates='user')

    def serialize(self):
        return{
            "id": self.id,
            "email": self.email
        }

class Planet(db.Model):    
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    favorites: Mapped[list['Favorite']] = relationship('Favorite', back_populates='planet')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            # do not serialize the password, its a security breach
        }

class People(db.Model):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship('Favorite', back_populates="people")

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "eye_color": self.eye_color
        }

class Favorite(db.Model):
    __tablename__ = 'favorite'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'), nullable=True)
    people_id: Mapped[int] = mapped_column(ForeignKey('people.id'), nullable=True)

    user: Mapped['User'] = relationship('User', back_populates='favorites')
    planet: Mapped['Planet'] = relationship('Planet', back_populates='favorites')
    people: Mapped['People'] = relationship('People', back_populates='favorites')

    def serialize(self):
        return{
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id
        }