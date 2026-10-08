
import argparse
import csv
import re
import subprocess
from pathlib import Path
from run_benchmarks import ROOT, SIZES, prepare, command, run


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repetitions', type=int, default=5)
    p.add_argument('--timeout', type=int, default=30)
    args = p.parse_args()

    build = prepare()

    if not Path('/usr/bin/time').exists():
        raise SystemExit('GNU /usr/bin/time is required (run on Linux).')

    rows = []

    for n in SIZES:
        for language in ('Python', 'Java', 'C'):
            cmd = command(language, n, build)
            run(cmd, args.timeout)

            for rep in range(1, args.repetitions + 1):
                proc = subprocess.run(
                    ['/usr/bin/time', '-v', *cmd],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=args.timeout
                )

                match = re.search(
                    r'Maximum resident set size \(kbytes\):\s*(\d+)',
                    proc.stderr
                )

                if not match:
                    raise RuntimeError('GNU time did not report peak RSS')

                _, size, _, checksum = next(
                    x for x in proc.stdout.splitlines()
                    if x.startswith('RESULT,')
                ).split(',')

                mib = int(match.group(1)) / 1024
                rows.append((language, int(size), rep, mib, int(checksum)))
                print(rows[-1], flush=True)

    path = ROOT / 'results/raw_memory_results.csv'

    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['language', 'n', 'repetition', 'peak_rss_mib', 'checksum'])
        writer.writerows(rows)

    print('Saved', path)


if __name__ == '__main__':
    main()
