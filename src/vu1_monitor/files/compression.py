import tarfile
from pathlib import Path


def make_tarfile(output_filename: Path, source_dir: Path) -> None:
    """Make a tarfile from all files in a directory

    :param output_filename: output filename (should be .tgz)
    :param source_dir: source directory to wrap into tar file
    """
    directory = source_dir.glob("**/*")
    files = [item for item in directory if item.is_file()]
    with tarfile.open(output_filename, "w:gz") as tar:
        for file in files:
            tar.add(file)


def extract_tarfile(tarfile_name: Path) -> None:
    """Extract a tarfile into a directory

    :param tarfile_name: name of tar file to extract
    """
    with tarfile.open(tarfile_name) as tar:
        tar.extractall()
