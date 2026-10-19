import argparse
import json
import resource
import sys

from mpi4py import MPI
from src.common import make_matrix, multiply_rows, checksum, split_rows


def peak_rss_mib():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    # macOS reports bytes; Linux reports KiB.
    if sys.platform == "darwin":
        return value / (1024 * 1024)
    return value / 1024


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("n", type=int)
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    workers = comm.Get_size()
    n = args.n

    comm.Barrier()
    start = MPI.Wtime()

    if rank == 0:
        a = make_matrix(n)
        b = make_matrix(n, 3)
        chunks = split_rows(a, workers)
    else:
        b = None
        chunks = None

    setup_end = MPI.Wtime()

    b = comm.bcast(b, root=0)
    local_a = comm.scatter(chunks, root=0)

    transfer_end = MPI.Wtime()

    local_c = multiply_rows(local_a, b)

    compute_end = MPI.Wtime()

    parts = comm.gather(local_c, root=0)

    gather_end = MPI.Wtime()

    local_metrics = {
        "rank": rank,
        "setup_s": setup_end - start,
        "distribution_s": transfer_end - setup_end,
        "compute_s": compute_end - transfer_end,
        "collection_s": gather_end - compute_end,
        "peak_rss_mib": peak_rss_mib()
    }

    all_metrics = comm.gather(local_metrics, root=0)

    if rank == 0:
        c = [row for part in parts for row in part]

        output = {
            "method": "distributed",
            "n": n,
            "workers": workers,
            "time_s": gather_end - start,
            "checksum": checksum(c),
            "max_worker_rss_mib": max(
                item["peak_rss_mib"] for item in all_metrics
            ),
            "sum_worker_rss_mib": sum(
                item["peak_rss_mib"] for item in all_metrics
            ),
            "max_setup_s": max(
                item["setup_s"] for item in all_metrics
            ),
            "max_distribution_s": max(
                item["distribution_s"] for item in all_metrics
            ),
            "max_compute_s": max(
                item["compute_s"] for item in all_metrics
            ),
            "max_collection_s": max(
                item["collection_s"] for item in all_metrics
            )
        }

        print("RESULT " + json.dumps(output))


if __name__ == "__main__":
    main()
