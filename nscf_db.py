import mysql.connector
from mysql.connector import errorcode


DB_NAME = 'nscf'

TABLES = {}

TABLES['rainfall'] = """
CREATE TABLE `rainfall` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rainfall_datetime` datetime NOT NULL,
  `station_id` int NOT NULL,
  `mm` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

TABLES['rainfall_stations'] = """
CREATE TABLE `rainfall_stations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `station_name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `station_name_UNIQUE` (`station_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

TABLES['river_heights'] = """
CREATE TABLE `river_heights` (
  `id` int NOT NULL AUTO_INCREMENT,
  `river_datetime` datetime NOT NULL,
  `station_id` int NOT NULL,
  `height` float NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

TABLES['river_stations'] = """
CREATE TABLE `river_stations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `station_name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `station_name_UNIQUE` (`station_name`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
"""

SQL = {}

SQL['insert_river_station'] = """
INSERT INTO river_stations (station_name)
VALUES (%s)
"""

SQL['insert_rainfall_station'] = """
INSERT INTO rainfall_stations (station_name) 
VALUES (%s)
"""

RIVER_HEIGHTS_STATIONS = [
    ["Breakfast Ck at Bowen Hills Rail #"],
    ["Brisbane R at City Gauge #"],
    ["Enoggera Ck at Bancroft Pk K Grove#"],
    ["Enoggera Reservoir #"],
    ["Enoggera Reservoir *"],
    ["Ithaca Ck at Jason St Ithaca *"]
]

RAINFALL_STATIONS = [
    ["Mt Coot-Tha AL *"],
    ["Mt Nebo AL *"]
]

def create_database(cursor, DB_NAME):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME)
        )
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


cnx = mysql.connector.connect(user='nscf_user', password='nScF1994!',
                      host='127.0.0.1', auth_plugin='mysql_native_password')
cursor = cnx.cursor()

try:
    cursor.execute("USE {}".format(DB_NAME))
    print("Using database {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exist.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor, DB_NAME)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)

for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

try:
    print("Adding river station data: ", end='')
    cursor.executemany(SQL["insert_river_station"], RIVER_HEIGHTS_STATIONS)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_DUP_ENTRY:
        print("already exists.")
    else:
        print(err.msg)
else:
    print("OK")

try:
    print("Adding rainfall station data: ", end='')
    cursor.executemany(SQL["insert_rainfall_station"], RAINFALL_STATIONS)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_DUP_ENTRY:
        print("already exists.")
    else:
        print(err.msg)
else:
    print("OK")

cnx.commit()
cursor.close()
cnx.close()
