import os


def get_num_core(num_core: int, num_inputs: int) -> int:
    """Function to get actual number of core."""

    if num_core > os.cpu_count():
        num_core = os.cpu_count() - 1 or os.cpu_count()

    if num_inputs < num_core:
        num_core = num_inputs

    return num_core
