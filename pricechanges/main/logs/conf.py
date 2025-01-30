from loguru import logger
import os


log_path = 'main/logs/errors.txt'

if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        pass

logger.add(log_path, format='{time} | {level} | {message} || Модуль: {file}, строка: {line}', level='ERROR')
#logger.add(sys.stderr, format='{time} | {level} | {message} || Модуль: {file}, строка: {line}', level='DEBUG')
