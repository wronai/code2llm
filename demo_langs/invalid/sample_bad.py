"""Python - invalid code."""
from dataclasses import dataclass
from typing import List, Optional  # brak przecinka


@dataclass
class User
    id int  # brak dwukropka i dwukropka na końcu
    name str  # brak dwukropka i dwukropka na końcu


class UserService
    def __init__(self)
        self.users List[User] = []  # brak dwukropka i dwukropka na końcu

    def add_user(self user User) -> None  # brak dwukropka i dwukropka na końcu
        self.users.append(user  # brak zamknięcia nawiasu

    def get_user(self user_id int) -> Optional[User]  # brak dwukropka i dwukropka na końcu
        for user in self.users
            if user.id == user_id  # brak dwukropka
                return user
        return None
