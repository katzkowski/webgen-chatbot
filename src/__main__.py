import logging
import logging.config
import sys

from .clustering.kmeans import run_training as kmeans_run_training
from .clustering.kmeans import test_pca_components
from .clustering.match_clusters import run_evaluation, run_matcher
from .crawling.crawler import init_crawler, run_crawler
from .crawling.screenshot_downloader import init_downloader, run_downloader
from .database.db_backup import create_db_backup
from .database.db_setup import format_labels_csv, init_db
from .dataset.conditional_dataset import create_dataset_json
from .dataset.dataset_creator import init_creator, run_creator
from .dataset.truncated_screenshots import remove_truncated_screenshots_from_db
from .logging_config import LOGGING_CONFIG


def main():
    logging.config.dictConfig(LOGGING_CONFIG)
    log = logging.getLogger("main")
    # log.info("Starting programm")

    # check if script has been specified
    if len(sys.argv) == 1:
        log.critical("No script specified, exiting program.")
        exit(1)

    # get script name
    script = sys.argv[1]

    # get script arguments
    args = sys.argv[2:]

    if len(args) == 0:
        # log.info("No command line arguments passed")
        pass
    else:
        log.info(f"Passed {len(args)} command line arguments")

    # run specified script
    if script == "init_db":
        if len(args) != 0:
            log.info(f"Calling script 'init_db' with arguments '{args}'")
            init_db(*args)
        else:
            log.info("Calling script 'init_db'")
            init_db()
    elif script == "create_db_backup":
        if len(args) != 0:
            log.info(f"Calling script 'create_db_backup' with argument '{args[0]}'")
            create_db_backup(args[0])
        else:
            log.info("Calling script 'create_db_backup'")
            create_db_backup()
    elif script == "format_labels_csv":
        log.info("Calling script 'format_labels_csv'")
        format_labels_csv()
    elif script == "init_crawler":
        log.info("Calling script 'init_crawler'")
        init_crawler()
    elif script == "run_crawler":
        if len(args) != 0:
            log.info(f"Calling script 'run_crawler' with argument '{args[0]}'")
            run_crawler(int(args[0]))
        else:
            log.info("Calling script 'run_crawler'")
            run_crawler()
    elif script == "init_downloader":
        log.info("Calling script 'init_downloader'")
        init_downloader()
    elif script == "run_downloader":
        log.info("Calling script 'run_downloader'")
        run_downloader()
    elif script == "run_creator":
        if len(args) != 0:
            log.info(f"Calling script 'run_creator' with arguments '{args}'")
            run_creator(args)
        else:
            log.info("Calling script 'run_creator' without arguments")
            run_creator()
    elif script == "init_creator":
        if len(args) != 0:
            log.info(f"Calling script 'init_creator' with arguments '{args}'")
            init_creator(args)
        else:
            log.info("Calling script 'init_creator' without arguments")
            init_creator()
    elif script == "rm_truncated":
        if len(args) != 0:
            log.info(f"Calling script 'rm_truncated' with argument '{args[0]}'")
            remove_truncated_screenshots_from_db(str(args[0]))
        else:
            log.info("Calling script 'rm_truncated'")
            remove_truncated_screenshots_from_db()
    elif script == "kmeans":
        if len(args) != 0:
            log.info(f"Calling script 'kmeans' with arguments '{args}'")
            kmeans_run_training(args)
        else:
            log.warning(f"Calling script 'kmeans' without arguments")
            kmeans_run_training()
    elif script == "test_pca_components":
        if len(args) != 0:
            log.info(f"Calling script 'test_pca_components' with arguments '{args}'")
            test_pca_components(args)
        else:
            log.warning(f"Calling script 'test_pca_components' without arguments")
            test_pca_components()
    elif script == "run_matcher":
        if len(args) != 0:
            log.info(f"Calling script 'run_matcher' with arguments '{args}'")
            run_matcher(args)
        else:
            log.warning(f"Calling script 'run_matcher' without arguments")
            run_matcher()
    elif script == "run_evaluation":
        if len(args) != 0:
            log.info(f"Calling script 'run_evaluation' with arguments '{args}'")
            run_evaluation(args)
        else:
            log.warning(f"Calling script 'run_evaluation' without arguments")
            run_evaluation()
    elif script == "create_dataset_json":
        if len(args) != 0:
            log.info(f"Calling script 'create_dataset_json' with arguments '{args}'")
            create_dataset_json(args)
        else:
            log.warning(f"Calling script 'create_dataset_json' without arguments")
            create_dataset_json()
    else:
        log.critical(f"Unknown script '{script}', exiting program.")
        exit(1)


if __name__ == "__main__":
    main()
