"""
COMP-5700 Exercise 16: ANGR Vulnerability Identification
Author: Jacob Murrah
Date: 12/5/2025
"""


import angr
import sys
import logging

logging.getLogger("cle").setLevel(logging.ERROR)


def main():
    angr_project = angr.Project("./comp5700", auto_load_libs=False)
    state = angr_project.factory.entry_state(
        add_options={angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY}
    )

    sim_manager = angr_project.factory.simulation_manager(state)
    sim_manager.explore(
        find=lambda s: b"sucessfully" in s.posix.dumps(sys.stdout.fileno())
    )

    if sim_manager.found:
        found_state = sim_manager.found[0]
        password = found_state.posix.dumps(sys.stdin.fileno()).strip(b"\x00").decode()
        output = found_state.posix.dumps(sys.stdout.fileno()).decode()

        clean_msg = output.replace("Enter password: ", "").strip()
        print(f"Found Correct Password: {password}")
        print(clean_msg)
    else:
        print("Could NOT find the correct password!")


if __name__ == "__main__":
    main()
