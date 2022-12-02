import time
import argparse


def main():
    """ Prints length of time it has been running every second until 60s has passed, then exit. """
    start_time = time.perf_counter()
    last_output_time = time.perf_counter() - 1

    while time.perf_counter() - start_time < 60:
        # Output time of last print greater than 1s
        if time.perf_counter() - last_output_time > 1:
            print(f"Time running: {time.perf_counter() - start_time:.1f}s")
            last_output_time = time.perf_counter()

    print(f"Done running with total time {time.perf_counter() - start_time}")


if __name__ == "__main__":
    # Takes no arguments
    parser = argparse.ArgumentParser()
    parser.parse_args()
    main()
