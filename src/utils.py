import yaml
import os

def load_config(config_file_name: str, base_dir: str = None) -> dict:
    """Safely read a Yaml configuration file as a dictionary.

    Args:
        config_file_name (str): Name of config file
        base_dir (str, optional): Path to directory with file. Defaults to 
        the ETL Base directory.

    Returns:
        dict: Dictionary of configuration values
    """
    if base_dir is None:
        base_dir = os.getcwd()

    file_path = os.path.join(
        base_dir,
        config_file_name
    )

    return load_yaml_file(file_path)


def load_yaml_file(file_path: str) -> dict:
    """Safely read in a YAML file as a dictionary

    Args:
        file_path (str): Path to yaml file

    Returns:
        dict: Dictionary of values from yaml file
    """
    with open(file_path, 'r') as stream:
        data_dict = yaml.safe_load(stream)
    return data_dict

