# -*- coding: utf-8 -*-
#

# region Import
import os.path
import sqlite3
import libs.logger_lib as logger

from contextlib import closing
# endregion Import


class SQLWorker:
    # default constructor
    def __init__(self, main_dir, db_filename):
        self.__db_file_path = os.path.join(main_dir, db_filename)
        pass

    @staticmethod
    def check_db_file_exist(main_dir, db_filename):
        """
        Метод проверки существования файла БД в каталоге data приложения. В случае отсутствия файла БД он будет
        создан. Также будет создана сама БД из 4-х таблиц: DimDate (Календарь), Accounts (Счета),
        Categories (Категории транзакций), Transactions (Транзакции пользователя) и выполнена первичная инициализация
        таблиц
        @param main_dir: основной каталог приложения
        @param db_filename: путь и имя файла базы данных
        @return:
        """
        db_file_path = os.path.join(main_dir, db_filename)

        if os.path.exists(db_file_path):
            logger.info("DB file is already exist")
            return

        sqlite_connection = None
        try:
            # файл БД не найден - выполняется создание файла БД, самой БД и их первоначальное заполнение
            logger.error("Application DB file", "Application DB doesn't exist. File creation started")
            sqlite_connection = sqlite3.connect(db_file_path)
            cursor = sqlite_connection.cursor()

            sql_scripts_path = os.path.join(main_dir, 'libs', 'sql_scripts')

            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_create_dim_date_table.sql')
            logger.info("DimDate table is created")
            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_initial_insert_into_dim_date.sql')
            logger.info("DimDate table is full")

            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_create_accounts_table.sql')
            logger.info("Accounts table is created")
            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_initial_insert_into_accounts.sql')
            logger.info("Accounts table is full")

            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_create_categories_table.sql')
            logger.info("Categories table is created")
            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_initial_insert_into_categories.sql')
            logger.info("Categories table is full")

            SQLWorker.execute_sql_script(cursor, sql_scripts_path, 'sql_create_transactions_table.sql')
            logger.info("Transactions table is created")

            cursor.close()
        except sqlite3.Error as err:
            logger.error("Application DB", err)
        except Exception as err:
            logger.error("Other error", err)
        finally:
            if sqlite_connection:
                sqlite_connection.close()

    @staticmethod
    def execute_sql_script(cursor, scripts_dir, script_file):
        """
        Метод выполнения sql-скрипта из из указанного файла
        @param cursor: курсор для выполнения запросов к БД
        @param scripts_dir: каталог, в котором находится инсполняемый sql-скрипт
        @param script_file: имя файла, содержащего sql-скрипт
        @return:
        """
        try:
            with closing(open(os.path.join(scripts_dir, script_file), 'r', encoding='utf-8')) as sqlite_file:
                sql_script = sqlite_file.read()
            cursor.executescript(u'{}'.format(sql_script))
        except Exception as err:
            logger.error(script_file, err)

    def __execute_sql_request(self, query):
        """
        Метод для выполнения запросов к БД приложения
        @param query: SQL-запрос в текстовом виде
        @return: результат выполнения SQL-запроса (возвращается массив кортежей)
        """
        sqlite_connection = None
        try:
            with sqlite3.connect(self.__db_file_path) as sqlite_connection:
                # sqlite_connection = sqlite3.connect(self.__db_file_path)
                cursor = sqlite_connection.cursor()

                cursor.execute(query)
                sqlite_connection.commit()
                records = cursor.fetchall()

                cursor.close()

            return records
        except sqlite3.Error as err:
            logger.error("Application DB", err)
        except Exception as err:
            logger.error("Other error", err)
        finally:
            if sqlite_connection:
                sqlite_connection.close()

    def make_select_for_categories_screen(self, from_date, to_date):
        """
        Метод получения выборки для заполнения данными страницы с категориями (Categories Screen). Вызывается при
        старте приложения, а также при обнвлении данных (при добавлении новых транзакций или изменении существующих)
        @param from_date: начальная дата диапазона
        @param to_date: конечная дата диапазона
        @return: результат выполнения SQL-запроса для заполнения данными страницы с категориями
        (возвращается массив кортежей). Результат выборки:
        0 - CategoryId - идентификатор категории расходов
        1 - CategoryName - наименование категории расходов
        2 - Icon - ниаменование иконки, используемой для обозначения категори расходов
        3 - CategoryScore - общая сумма трат по категории за выбранный период
        4 - CategoryColor - цвет, используемый для обозначения расходов по конкретной категории на диаграммах
        """
        query = \
            f"""
            WITH t_score AS (
                SELECT
                    trans.CategoryId
                    ,SUM(trans.TransactionScore) as CategoryScore
                FROM Transactions as trans
                LEFT JOIN DimDate as ddates on ddates.DateKey = trans.DateKey
                WHERE ddates.FullDate between '{from_date}' AND '{to_date}'
                GROUP BY trans.CategoryId
            )
            SELECT
                categ.CategoryId
                ,categ.CategoryName
                ,categ.Icon
                ,ifnull(t_score.CategoryScore, 0) as CategoryScore
                ,categ.CategoryColor
            FROM Categories as categ
            LEFT JOIN t_score on t_score.CategoryId = categ.CategoryId
            """
        return self.__execute_sql_request(query)

    def make_select_for_transactions_screen(self, from_date, to_date, sort_type='DESC'):
        """
        Метод получения выборки для заполнения данными страницы с транзакциями (Transactions Screen). Вызывается при
        старте приложения, а также при обнвлении данных (при добавлении новых транзакций или изменении существующих)
        @param from_date: начальная дата диапазона
        @param to_date: конечная дата диапазона
        @param sort_type: порядок сортировки результирующей выборки: desc - по убыванию, asc - по возрастанию
        @return: результат выполнения SQL-запроса для заполнения данными страницы с транзакциями
        (возвращается массив кортежей). Результат:
        0 - Icon - ниаменование иконки, используемой для обозначения категори расходов
        1 - CategoryName - наименование категории расходов
        2 - TransactionScore - сумма транзакции
        3 - TransactionNote - заметка, добавленная к транзакции
        4 - TransactionId - идентификатор транзакции
        5 - FullDate - полная дата совершания транзакции
        6 - CategoryColor - цвет, используемый для обозначения расходов по конкретной категории на диаграммах
        """
        query = \
            f"""
            SELECT
                categ.Icon
                ,categ.CategoryName
                ,trans.TransactionScore
                ,trans.TransactionNote
                ,trans.TransactionId
                ,ddates.FullDate
                ,categ.CategoryColor
            FROM Transactions as trans
            LEFT JOIN Categories as categ on categ.CategoryId = trans.CategoryId
            LEFT JOIN DimDate as ddates on ddates.DateKey = trans.DateKey
            WHERE ddates.FullDate between '{from_date}' AND '{to_date}'
            ORDER BY ddates.FullDate {sort_type}
            """
        return self.__execute_sql_request(query)

    def make_select_for_statistics_screen(self, from_date, to_date):
        """
        Не используется
        Метод получения выборки для заполнения данными страницы со статистикой (Statistics Screen). Вызывается при
        старте приложения, а также при обнвлении данных (при добавлении новых транзакций или изменении существующих)
        @param from_date: начальная дата диапазона
        @param to_date: конечная дата диапазона
        @return: результат выполнения SQL-запроса для заполнения данными страницы со статистикой
        (возвращается массив кортежей).
        """
        query = \
            f"""
            SELECT
                ddates.FullDate
                ,categ.CategoryName
                ,categ.CategoryColor
                ,trans.TransactionScore
            FROM Transactions as trans
            LEFT JOIN Categories as categ on categ.CategoryId = trans.CategoryId
            LEFT JOIN DimDate as ddates on ddates.DateKey = trans.DateKey
            WHERE ddates.FullDate between '{from_date}' AND '{to_date}'
            ORDER BY ddates.FullDate DESC
            """
        return self.__execute_sql_request(query)

    def get_category_id(self, category_name):
        """
        Метод, используемый для получения идентификатора категории расходов из БД.
        @param category_name: наименование категории расходов, для которой необходимо определить идентификатор
        @return: результат выполнения SQL-запроса - картеж из двух элементов: 0 - идентификатор категории расходов,
        1 - наименование категории расходов
        """
        query = \
            f"""
            SELECT
                categ.CategoryId
                ,categ.CategoryName
            FROM Categories as categ
            WHERE categ.CategoryName = '{category_name}'
            """
        return self.__execute_sql_request(query)

    def get_all_category(self):
        """
        Метод, используемый для формировния выборки со всеми категориями расходов данными об этих категориях.
        @return: результат выполнения SQL-запроса - список картежей, каждеый из которых содержит два элемента:
        0 - наименование категории расходов, 1 - цвет, используемый для обозначения расходов по категории на диаграммах
        """
        query = \
            f"""
            SELECT
                categ.CategoryName
                ,categ.CategoryColor
            FROM Categories as categ
            """
        return self.__execute_sql_request(query)

    def insert_new_transaction_data(self, transaction_data):
        """
        Метод, используемый для добавления новых транзакци с расходами в БД.
        @param transaction_data: данные о новых расходах. AccountId - идентификатор счета, CategoryId - идентификатор
        категории расходов, DateKey - идентификатор даты транзакции, TransactionScore - сумма транзакции,
        TransactionNote - заметка к транзакции
        @return: None
        """
        query = \
            f"""
            INSERT INTO Transactions (CategoryId, DateKey, TransactionScore, TransactionNote)
            VALUES {transaction_data}
            """
        return self.__execute_sql_request(query)

    def update_transaction_data(self, transaction_data):
        """
        Метод, используемый для обновления данных о расходах в БД.
        @param transaction_data: данные об обновляемой транзакции, а также новые данные о ней. CategoryId -
        идентификатор категории расходов, DateKey - идентификатор даты транзакции, TransactionScore - сумма транзакции,
        TransactionNote - заметка к транзакции, TransactionId - идентификатор обновляемой транзакции.
        @return: None
        """
        query = \
            f"""
            UPDATE Transactions
            SET
                CategoryId = {transaction_data[0]},
                DateKey = '{transaction_data[1]}',
                TransactionScore = {transaction_data[2]},
                TransactionNote = '{transaction_data[3]}'
            WHERE TransactionId = {transaction_data[4]}
            """
        return self.__execute_sql_request(query)

    def delete_transaction_data(self, transaction_data):
        """
        Метод, используемый для удаления транзакций с расходами из БД.
        @param transaction_data: данные о удаляемой транзакции. TransactionId - идентификатор удаляемой транзакции,
        DateKey - идентификатор даты удаляемой транзакции
        @return: None
        """
        query = \
            f"""
            DELETE FROM Transactions
            WHERE 1=1
                AND TransactionId = {transaction_data[0]}
                AND DateKey = '{transaction_data[1]}'
            """
        return self.__execute_sql_request(query)
