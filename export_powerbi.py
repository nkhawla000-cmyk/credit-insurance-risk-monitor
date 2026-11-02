"""Build reproducible CSVs for Power BI; run after `python3 run.py`."""
from src.bi_export import export
if __name__ == '__main__':
    from pprint import pprint
    pprint(export())
