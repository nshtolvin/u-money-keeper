# U-Money-Keeper

The project of a simple application for keeping track of your daily expenses.

## App Screenshots
<img src="./screenshots/dashboard.png" width="48%"/> <img src="./screenshots/statistics.png" width="48%"/>

<img src="./screenshots/navigation.png" width="32%"/> <img src="./screenshots/transactions.png" width="48%"/>

## Built With
* [Kivy Framework](https://github.com/kivy/kivy) - UI Elements
* [KivyMD Framework](https://github.com/kivymd/KivyMD) - Material Design UI Elements
* [SqLite](https://www.sqlite.org/index.html) - Local DB
* [sqlite3 python](https://docs.python.org/3/library/sqlite3.html) - Local DB API
* [Icons](https://www.flaticon.com/) - All app's icons
* [Charts](https://github.com/matplotlib/matplotlib) - All app's Charts

## Requirements (Installation)
You need the [following](requirements.txt) libraries to use the project.

Installation:
1. Create a virtual environment
```virtualenv venv```
2. Activate virtual environment with the command
```source venv/bin/activate``` (Linux) или ```venv\Scripts\activate.bat``` (Windows)
3. Install __Kyvy__ library with dependent packages with the command
```pip install kivy```
4. Install __KyvyMD__ library with dependent packages with the command
```pip install kivymd```
5. Install __matplotlib__ (version < 3.3.0) library with dependent packages with the command
```pip install matplotlib==3.2.2```
6. Add __matplotlib__ library to __Kyvy__ with the command
```garden install matplotlib```

## Authors

* **Nikita** - [GitHub](https://github.com/nshtolvin)