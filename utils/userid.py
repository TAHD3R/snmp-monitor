from exceptions.notifier import UserIdError


def convert_userid(userid: str, decrypt: bool = False) -> str:
    if decrypt:
        year = str(int(userid[10:12]) + 1945)
        no = str(int(userid[2:9]) - 115342)
        no = no[1:7]
        userid = year + no
    else:
        userid = (
            "8"
            + userid[2:3]
            + str(int(userid[-6:]) + 1115342)
            + userid[8:9]
            + str(int(userid[0:4]) - 1945)
        )
    return userid


def is_encrypted(userid: str) -> bool:
    if len(userid) == 12:
        return True
    elif len(userid) == 10:
        return False
    else:
        raise UserIdError
