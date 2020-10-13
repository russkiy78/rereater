from datetime import datetime, timezone
import os.path
from os import path

from configobj import ConfigObj

CONFIG_FILE = "./config.ini"


def main():
    # get config from file
    try:
        config = ConfigObj(CONFIG_FILE)
    except OSError:
        print("Config read error")
        return False

    # start to log
    try:
        log_file = open(
            path.join(config['general']['LOG_PATH'], datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f.log')), 'w')
    except OSError:
        print("Failed to open log file error")
        return False

    for file in os.listdir(config['general']['UPDATE_DIR_PATH']):
        if file.endswith(".cdr"):

            # open the next small file
            small_file_path = path.join(config['general']['UPDATE_DIR_PATH'], file)
            with open(small_file_path, 'r') as small_fp:
                small_lines_counter = 0
                for line_from_small in small_fp:
                    small_lines_counter += 1
                    print("line", small_lines_counter)
                    list_line_for_small = line_from_small.rstrip().split('?')
                    founded_datetime = datetime.fromtimestamp(int(list_line_for_small[3]) / 1000000, timezone.utc)

                    # day dir path for search
                    replace_day_dir_path = path.join(config['general']['CDR_DIR_PATH'],
                                                     founded_datetime.strftime('%Y'),
                                                     founded_datetime.strftime('%m'),
                                                     founded_datetime.strftime('%d')
                                                     )

                    # if day folder exist
                    if path.exists(replace_day_dir_path):

                        # go for all hours folders
                        hour_from_line = int(founded_datetime.strftime('%H'))
                        replaced = False
                        for hours_dir in os.listdir(replace_day_dir_path):

                            if replaced:
                                break

                            if int(hours_dir) != hour_from_line:
                                continue

                            # and for all files inside them
                            for big_file in os.listdir(path.join(replace_day_dir_path, hours_dir)):

                                if big_file.endswith(".cdr"):

                                    # open the big file
                                    new_big_file_data = []

                                    replace_path = path.join(replace_day_dir_path, hours_dir, big_file)
                                    with open(replace_path, 'r') as big_fp:
                                        big_lines_counter = 0
                                        for line_from_big in big_fp:
                                            big_lines_counter += 1
                                            list_line_for_big = line_from_big.rstrip().split('?')
                                            if list_line_for_big[13] == list_line_for_small[16] \
                                                    and list_line_for_big[23] == list_line_for_small[35]:
                                                newline = list_line_for_big
                                                newline[41] = list_line_for_small[60]
                                                newline[48] = list_line_for_small[67]
                                                new_big_file_data.append(newline)
                                                log_file.write(
                                                    "[%s] Line #%d in file [%s] is replaced to line #%d in file [%s]. Now: 41=[%s] 48=[%s] \n" %
                                                    (datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                     big_lines_counter,
                                                     replace_path,
                                                     small_lines_counter,
                                                     small_file_path,
                                                     str(list_line_for_small[60]),
                                                     str(list_line_for_small[67]),
                                                     ))
                                                log_file.flush()
                                                replaced = True
                                            else:
                                                new_big_file_data.append(list_line_for_big)

                                    # finally write a new big file
                                    if replaced:
                                        if config['general']['DEBUG'] == "1":
                                            replace_path_to_save = replace_path + ".copy"
                                        else:
                                            replace_path_to_save = replace_path
                                        with open(replace_path_to_save, 'w') as replace_fp_write:
                                            for item in new_big_file_data:
                                                replace_fp_write.write("%s\n" % '?'.join(item))

            log_file.close()


if __name__ == '__main__':
    main()
