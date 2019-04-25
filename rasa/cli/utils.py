import os
from typing import Any, Callable, Dict, Optional, Text, List

from rasa.constants import DEFAULT_MODELS_PATH, CONFIG_MANDATORY_KEYS


def get_validated_path(
    current: Optional[Text],
    parameter: Text,
    default: Optional[Text] = None,
    none_is_valid: bool = False,
) -> Optional[Text]:
    """Check whether a file path or its default value is valid and returns it.

    Args:
        current: The parsed value.
        parameter: The name of the parameter.
        default: The default value of the parameter.
        none_is_valid: `True` if `None` is valid value for the path,
                        else `False``

    Returns:
        The current value if it was valid, else the default value of the
        argument if it is valid, else `None`.
    """

    if current is None or current is not None and not os.path.exists(current):
        if default is not None and os.path.exists(default):
            print_warning(
                "'{}' not found. Using default location '{}' instead."
                "".format(current, default)
            )
            current = default
        elif none_is_valid:
            current = None
        else:
            cancel_cause_not_found(current, parameter, default)

    return current


def is_valid_config(path: Text, mandatory_keys: List[Text]) -> bool:
    import rasa.utils.io

    config_data = rasa.utils.io.read_yaml_file(path)

    for k in mandatory_keys:
        if k not in config_data or config_data[k] is None:
            return False

    return True


def cancel_cause_not_found(
    current: Optional[Text], parameter: Text, default: Optional[Text]
) -> None:
    """Exits with an error because the given path was not valid.

    Args:
        current: The path given by the user.
        parameter: The name of the parameter.
        default: The default value of the parameter.

    """

    default_clause = ""
    if default:
        default_clause = "use the default location ('{}') or ".format(default)
    print_error(
        "The path '{}' does not exist. Please make sure to {}specify it"
        " with '--{}'.".format(current, default_clause, parameter)
    )
    exit(1)


def parse_last_positional_argument_as_model_path() -> None:
    """Fixes the parsing of a potential positional model path argument."""
    import sys

    if (
        len(sys.argv) >= 2
        and sys.argv[1] in ["run", "test", "shell", "interactive"]
        and not sys.argv[-2].startswith("-")
        and os.path.exists(sys.argv[-1])
    ):
        sys.argv.append(sys.argv[-1])
        sys.argv[-2] = "--model"


def create_output_path(
    output_path: Text = DEFAULT_MODELS_PATH, prefix: Text = ""
) -> Text:
    """Creates an output path which includes the current timestamp.

    Args:
        output_path: The path where the model should be stored.
        prefix: A prefix which should be included in the output path.

    Returns:
        The generated output path, e.g. "20191201-103002.tar.gz".
    """
    import time

    if output_path.endswith("tar.gz"):
        return output_path
    else:
        time_format = "%Y%m%d-%H%M%S"
        file_name = "{}{}.tar.gz".format(prefix, time.strftime(time_format))
        return os.path.join(output_path, file_name)


def minimal_kwargs(kwargs: Dict[Text, Any], func: Callable) -> Dict[Text, Any]:
    """Returns only the kwargs which are required by a function.

    Args:
        kwargs: All available kwargs.
        func: The function which should be called.

    Returns:
        Subset of kwargs which are accepted by `func`.

    """
    from rasa.utils.common import arguments_of

    possible_arguments = arguments_of(func)

    return {k: v for k, v in kwargs.items() if k in possible_arguments}


def print_success(text: Text):
    print_color(text, bcolors.OKGREEN)


class bcolors(object):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def wrap_with_color(text: Text, color: Text):
    return color + text + bcolors.ENDC


def print_color(text: Text, color: Text):
    print (wrap_with_color(text, color))


def print_warning(text: Text):
    print_color(text, bcolors.WARNING)


def print_error(text: Text):
    print_color(text, bcolors.FAIL)
