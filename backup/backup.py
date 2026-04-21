import datetime
import logging
import os
import zipfile

def create_backup(log: logging.Logger, sources: list[str], 
                  destination: str) -> str:
    """
    Compresses all files from the source directories into a single
    timestamped zip archive in the destination folder.

    Args:
        log:                A configured logger instance.
        source_directories: A list of validated source directory paths.
        destination:        The folder path where the archive will be saved.

    Returns:
        The full file path of the created archive as a string.

    Raises:
        Exception: Re-raises any error that occurs during the zip operation.
    """

    # Step 1: Create an unique filepath for the zip file and create the filepath
    time_of_backup = datetime.datetime.now()
    backup_filename = time_of_backup.strftime("backup_%Y-%m-%d_%H-%M-%s.zip")
    backup_filepath = os.path.join(destination, backup_filename)

    # Step 2: Verify the existence of the destination directory
        # exist_ok=True prevents an error from being thrown if the directory 
        # already exists
    os.makedirs(destination, exist_ok=True)

    # Step 3: Using os.walk, traverse each source and add each filepath to the zip
    try:
        with zipfile.ZipFile(backup_filepath, "w") as backup:
            for source in sources:
                # Ignore subfolders, just a part of os.walk
                for current_folder, subfolders, filenames in os.walk(source):
                    for filename in filenames:
                        filepath = os.path.join(current_folder, filename)
                        backup.write(filepath, arcname=filename)
    except Exception as error:
        log.error(f"Backup could not be completed: {error}")
        raise

    # Step 4: Log success
    log.info(f"Backup {backup_filename} successfully created in {destination}")

    return backup_filepath

def discover_sources(log: logging.Logger, sources: list[str]) -> list[str]:
    """
    Validates a list of directory paths and returns only those that
    exist and are readable on the filesystem.

    Args:
        log:                A configured logger instance.
        source_directories: A list of directory path strings to validate.

    Returns:
        A list of valid directory path strings.

    Raises:
        ValueError: If none of the provided paths are valid directories.
    """

    valid_sources = []

    # Step 1: Determine if each source is valid
    for source in sources:

        print(os.path.exists(source))
        print(os.path.isdir(source))

        # Log "INFO" for success
        if os.path.exists(source) and os.path.isdir(source):
            valid_sources.append(source)
            log.info(f"Directory successfully found. Filepath: {source}")

        # Log "WARNING" for failure – continue loop
        else:
            log.warning(f"Directory could not be found. Skipping filepath: {source}")

    # Step 2: Throw an error if there are no valid sources
    if not valid_sources:
        raise ValueError("Error: no directories found. Backup cannot be completed.")
    
    return valid_sources

def rotate_old_backups(log: logging.Logger, destination: str, 
                       max_backups: int) -> None:
    """
    Deletes the oldest backup archives from the destination folder
    when the total count exceeds max_backups.

    Args:
        log:         A configured logger instance.
        destination: The folder path where backup archives are stored.
        max_backups: The maximum number of archives to retain.
    """
    
    # Step 1: Find all .zip files in the destinaiton directory
    zips = [os.path.join(destination, filename) 
        for filename in os.listdir(destination) 
        if filename.endswith(".zip")]

    # Step 2: Sort the backups by age
    zips = sorted(zips, key=os.path.getmtime)

    # Step 3: Delete old backups
    number_of_backups = len(zips)
    number_to_remove = max(0, number_of_backups - max_backups)
    backups_to_remove = zips[:number_to_remove]

    if backups_to_remove:
        for backup in backups_to_remove:
            try:
                os.remove(backup)
                log.info(f"Old backup deleted. {backup}")
            except Exception as error:
                log.warning(f"Could not delete old backup {backup}: {error}")
    else:
        log.info(f"No backups to be removed. {number_of_backups}/{max_backups} backups")

def setup_logger() -> logging.Logger:

    # Step 1: Initialize the logger
    logger = logging.getLogger(__name__)

    # Step 2: Configure the level
    logger.setLevel(logging.INFO) # The type of messages to be shown. Shows that
                                  # level and all types above.
                                  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Step 3: Initialize a formatter
    log_formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Step 4: Initialize handlers and attach formatter
    file_handler = logging.FileHandler("backup.log")
    stream_handler = logging.StreamHandler()

    file_handler.setFormatter(log_formatter)
    stream_handler.setFormatter(log_formatter)

    # Step 5: Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

def main() -> int:
    """
    Orchestrates the full backup run. Calls each stage in order and
    handles any exceptions that were not caught by the individual functions.

    Returns:
        0 if the backup completed successfully, 1 if it failed.
    """

    # Step 1: Initialize the logger so that every subsequent step can be recorded.
    log = setup_logger()

    # Step 2: Configuration
    destination = ""
    sources = []
    max_backups = 5

    # Step 3: Backup and log any errors
    try:
        valid_sources = discover_sources(log, sources)
        backup = create_backup(log, valid_sources, destination)
        rotate_old_backups(log, destination, max_backups)
    except ValueError as error:
        log.error(f"An unexpected value error stopped the backup: {error}")
        return 1
    except Exception as error:
        log.error(f"An unexpected error stopped the backup: {error}")
        return 1

    # Step 4: Log success
    log.info(
        f"Backup complete with no runtime errors. Backup: {backup} — Location: {destination}."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())