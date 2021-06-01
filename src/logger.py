import sys

from loguru import logger


def formatter(record):
    lines = record["message"].splitlines()
    prefix = "{time} - {level} - {function} - ".format(**record)

    if len(lines) > 1:
        indented = lines[0] + "\n" + "\n".join(" " * len(prefix) + line for line in lines[1:])
    else:
        indented = lines[0] + "\n".join(" " * len(prefix) + line for line in lines[1:])
    record["extra"]["indented"] = indented
    return "<g>{time}</> - <lvl>{level}</> - <e>{function}</> - <lvl>{extra[indented]}</>\n{exception}"


logger.remove()
logger.add(sys.stderr, format=formatter)
