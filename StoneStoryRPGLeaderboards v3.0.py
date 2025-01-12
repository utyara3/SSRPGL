#--------------БИБЛИОТЕКИ---------------
from pandas import read_html
from prettytable import PrettyTable
from pyfiglet import figlet_format
from os import system, mkdir
from os.path import exists
from pystyle import Colorate, Colors
import json
from tqdm import tqdm
from colorama import init, Fore, Style

init()

#-------ОСНОВНОЙ-КЛАСС-ТАБЛИЦЫ-ЛИДЕРОВ-------
class Leaderboard:
    def __init__(self):
        self.table = PrettyTable()
        self.table.field_names = ["Место", "Имя", "Время", "Мощность"]
        self.location = ""
        self.location_ru = ""
        self.users_list = {}
        self.all_data = []

    #Загрузить данные о локации
    def load_location(self, location):
        self.location, self.location_ru = location
        self.address = f"https://ssrpgleaderboards.up.railway.app/location/{self.location}"
        self.users_list = {self.location : {}}

        #Парс локации
        for url in tqdm([self.address]):
            all_users = read_html(self.address)

        count = 0
        for users_by_stars in all_users:
            #Звезды
            count += 5
            #Представление данных
            self.users_list[self.location][count] = {"users" : []}
            for user in users_by_stars.to_numpy():
                user = user.tolist()
                user[0] = int(user[0])
                self.users_list[self.location][count]["users"].append({
                        "place" : user[0],
                        "name" : user[1],
                        "time" : user[2],
                        "gp" : user[3]
                        })

        return self.users_list

    #Загрузить данные о всех локациях
    def load_locations(self, locations):
        self.all_data = []
        for location, location_ru in locations.items():
            self.all_data.append(self.load_location([location, location_ru]))
        return self.all_data

#Основной экземпляр
lb = Leaderboard()


#Все локации
locations = {
    "rocky_plateau":"Каменное Плато", 
    "deadwood_valley":"Каньон Дедвуд", 
    "caustic_caves":"Пещеры Страха", 
    "fungus_forest":"Грибной Лес", 
    "undead_crypt":"Призрачные Залы",
    "bronze_mine":"Бурлящие Шахты", 
    "icy_ridge":"Ледяной Хребет", 
    "temple":"Храм"
}


#Глобальные состояния (сохранялка)
states = {
    "action" : ("Главное меню", "")
}


#PressEnterToContinue
def petc():
    input("Нажмите Enter чтобы продолжить...")


def check_files():
    if not exists("data"):
        mkdir(f"data")
        print(f"Создал папку data")
    for loc in locations.keys():
        if not exists(f"data/{loc}.json"):
            open(f"data/{loc}.json", "w").close()
            print(f"Файл data/{loc}.json) создан.")


#Меню при входе
def main_menu():
    print("""
[1] Выбрать локацию
[2] Выход""")


#Меню выбора локации
def choose_location():
    print("""
[1] Каменистое Плато
[2] Каньон Дедвуд
[3] Пещеры Страха
[4] Грибной Лес
[5] Призрачные залы
[6] Бурлящие шахты
[7] Ледяной хребет
[8] Храм

[9] Назад
[10] Выход""")


#Основное меню для работы с одной локацией
def location_menu():
    print(f"""
Текущая локация: {lb.location_ru}

[1] Таблица пользователей
[2] Найти пользователя
[3] Изменить локацию
[4] Отслеживание пользователей
[5] Выход""")


def users_table_menu():
    print("""
Выберите звезды:
[1] 5*
[2] 10*
[3] 15*
[4] 20*
[5] Все звезды

[6] Назад""")

    return "location_menu"


#Загрузка локации
def load_location(location):
    #Есть lb.location, так что это пока не надо
    #states["current_location"] = location
    lb.load_location([location, locations[location]])

    petc()

    return "location_menu"


def leaderboard_table(stars):
    for loc, loc_info in lb.users_list.items():
        for star, star_info in loc_info.items():
            if star == stars or stars == "all":
                print(f"\n{star}*")
                for users, users_info in star_info.items():
                    for user_info in users_info:
                        lb.table.add_row(user_info.values())
                print(lb.table)
                lb.table.clear_rows()


    petc()

    return "location_menu"

def search_user(user=""):
    is_petc = False
    if not user:
        is_petc = True
        user = input("\nВведите имя пользователя: ")
    ret_list = {}
    for loc, loc_info in lb.users_list.items():
        for star, star_info in loc_info.items():
            find = False
            for users, users_info in star_info.items():
                for user_info in users_info:
                    if user_info["name"] == user:
                        lb.table.add_row(user_info.values())
                        if user_info["name"] not in ret_list:
                            ret_list[user_info["name"]] = {}
                        ret_list[user_info["name"]][star] = {"user": user_info}
                        find = True
            if find:
                print(f"\n{star}*")
                print(lb.table)
            else:
                print(f"Пользователь не найден в топ 50 на локации {lb.location_ru} {star}*")
            lb.table.clear_rows()
    if is_petc:
        petc()
    return ret_list


def view_tracked_users():
    users = []
    with open(f"data/{lb.location}.json", "r+", encoding="utf-8") as file:
        try:
            file_users = json.load(file)
            file.seek(0)
            for user in file_users.keys():
                users.append(user)

            if users:
                print(f"Отслеживаемые пользователи: {', '.join(users)}")
            else:
                print("Никто не отслеживается")

        except json.decoder.JSONDecodeError:
            print("Никто не отслеживается")

    petc()


def compare_track_user():
    tracked_user = input("Введите имя пользователя: ")
    diff = []
    find = False
    with open(f"data/{lb.location}.json", "r+", encoding="utf-8") as file:
        try:
            file_users = json.load(file)
            file.seek(0)
            for loc, loc_info in lb.users_list.items():
                    for star, star_info in loc_info.items():
                        for users, users_info in star_info.items():
                            for user_info in users_info:
                                if user_info["name"] in file_users and user_info["name"] == tracked_user:
                                    find = True
                                    if list(file_users[user_info["name"]][str(star)]["user"].values()) != list(user_info.values()):
                                        print(f"\n\n{star}*")
                                        print("\nБыло:\n")
                                        lb.table.add_row(file_users[user_info["name"]][str(star)]["user"].values())
                                        print(lb.table)
                                        lb.table.clear_rows()
                                        print("\nСтало:\n")
                                        lb.table.add_row(user_info.values())
                                        print(lb.table)
                                        lb.table.clear_rows()
                                    else:
                                        print(f"\n\n{star}*")
                                        print("Ничего не изменилось.")

        except json.decoder.JSONDecodeError:
            print("Никто не отслеживается")
    if not find:
        print(f"{tracked_user} не отслеживается.")
    petc()


def track_new_user():
    tracked_user = input("Введите имя пользователя: ")
    find = False
    file_users = {}
    with open(f"data/{lb.location}.json", "r+", encoding="utf-8") as file:
        try:
            file_users = json.load(file)
        except json.decoder.JSONDecodeError:
            file_users = {}

        for loc, loc_info in lb.users_list.items():
            for star, star_info in loc_info.items():
                for users, users_info in star_info.items():
                    for user_info in users_info:
                        if user_info["name"] == tracked_user:
                            find = True
                            if user_info["name"] not in file_users:
                                file_users[user_info["name"]] = {}
                            if str(star) not in file_users[user_info["name"]] or \
                               file_users[user_info["name"]][str(star)]["user"] != user_info:
                                file_users[user_info["name"]][str(star)] = {"user": user_info}

        file.seek(0)
        file.truncate()
        json.dump(file_users, file, ensure_ascii=False, indent=4)

        if find:
            print(f"\nДанные о пользователе {tracked_user} сохранены!")
        else:
            print(f"\n{tracked_user} нет в таблице лидеров {lb.location_ru} в топ 50.")

    petc()


def stop_tracking_user():
    tracked_user = input("Введите имя пользователя: ")
    with open(f"data/{lb.location}.json", "r+", encoding="utf-8") as file:
        try:
            file_users = json.load(file)
            if tracked_user in file_users.keys():
                del file_users[tracked_user]
                print("Данные успешно удалены.")
            else:
                print(f"{tracked_user} не отслеживается.")
            
            file.seek(0)
            file.truncate()
            json.dump(file_users, file, ensure_ascii=False, indent=4)

        except json.decoder.JSONDecodeError:
            print("Никто не отслеживается.")

    petc()


def track_user_menu():
    print("""
[1] Посмотреть отслеживаемых пользователей
[2] Сравнить сохраненные данные с новыми
[3] Отслеживать нового пользователя | Обновить данные о пользователе
[4] Перестать отслеживать пользователя
[5] Назад

[6] Выход""")


#Карта программы
menus = {
    #Название меню
    "main" : {
        #Функция вывода этого меню
        "menu" : main_menu,
        "options" : {
            #Опции
            "1" : ("Выбор локации", "choose_location_menu"),
            "2" : ("Выход", quit)
        }
    },
    "choose_location_menu" : {
        "menu" : choose_location,
        "options" : {
            "1" : ("Каменистое Плато", lambda: load_location("rocky_plateau")),
            "2" : ("Каньон Дедвуд", lambda: load_location("deadwood_valley")),
            "3" : ("Пещеры Страха", lambda: load_location("caustic_caves")),
            "4" : ("Грибной Лес", lambda: load_location("fungus_forest")),
            "5" : ("Призрачные Залы", lambda: load_location("undead_crypt")),
            "6" : ("Бурлящие Шахты", lambda: load_location("bronze_mine")),
            "7" : ("Ледяной Хребет", lambda: load_location("icy_ridge")),
            "8" : ("Храм", lambda: load_location("temple")),
            "9" : ("Назад", "main"),
            "10" : ("Выход", quit)
        }
    },
    "location_menu" : {
        "menu" : location_menu,
        "options" : {
            "1" : ("Таблица пользователей", "users_table_menu"),
            "2" : ("Найти пользователя", search_user),
            "3" : ("Изменить локацию", "choose_location_menu"),
            "4" : ("Отслеживание пользователей", "track_user_menu"),
            "5" : ("Выход", quit)
        }
    },

    "users_table_menu" : {
        "menu" : users_table_menu,
        "options" : {
            "1": ("5*", lambda: leaderboard_table(5)),
            "2": ("10*", lambda: leaderboard_table(10)),
            "3": ("15*", lambda: leaderboard_table(15)),
            "4": ("20*", lambda: leaderboard_table(20)),
            "5": ("Все звезды", lambda: leaderboard_table("all")),
            "6": ("Назад", "location_menu")
        }

    },

    "track_user_menu" : {
        "menu" : track_user_menu,
        "options" : {
            "1" : ("Посмотреть отслеживаемых пользователей", view_tracked_users),
            "2" : ("Сравнить сохраненные данные с новыми", compare_track_user),
            "3" : ("Отслеживать нового пользователя", track_new_user),
            "4" : ("Перестать отслеживать пользователя", stop_tracking_user),
            "5" : ("Назад", "location_menu"),
            "6" : ("Выход", quit)

        }
    }
}
    

#Навигация по карте
def navigate_menu(current_menu="main"):
    while 1:
        system("cls")
        print(Colorate.Horizontal(Colors.purple_to_blue, figlet_format("StoneStory\nLeaderboard")))
        print(Fore.CYAN+f"Выбранный пункт: {states['action'][0]}")
        #Менюшка
        menu = menus[current_menu]
        menu["menu"]()

        choice = input("\n[?] Выберите опцию: ").strip()

        #Проверяем опцию на наличие
        if choice in menu["options"]:
            states["action"] = menu["options"][choice]
            

            if callable(states["action"][1]):  #Если это функция, то вызываем
                result = states["action"][1]()  # Сохраняем результат выполнения
                if isinstance(result, str):  # Если функция возвращает имя меню
                    current_menu = result

            elif states["action"][1] == "exit":
                print(Fore.RED + "Выход")
                return

            else:
                current_menu = states["action"][1] #Менюшка

        else:
            print(Fore.YELLOW + "Такого пункта нет, попробуйте снова.")
            petc()


if __name__ == '__main__':
    print("Проверяю целостность файлов..")
    check_files()
    print("Файлы проверены.")
    navigate_menu()

print(Style.RESET_ALL)
