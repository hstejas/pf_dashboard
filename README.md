# Personal finance dashboard

## Support for banks and statement

| Bank                | statement type | format |
| ------------------- | -------------- | ------ |
| State Bank Of India | SB, PPF, Loan  | csv    |
| Canara Bank         | SB             | csv    |
| ICICI Bank          | SB             | xls    |
| PhonePe             | UPI            | pdf    |

## Usage

### Parsing all data

1. Clone
2. `pip install -r requirements.txt`
3. Copy account statements into `./data/<bank>/`, same abbrev as `pf/plugins/*.py`
4. Create `./data/.passwords`, one password per line.
5. run `./main.py`

### Visualizing data

1. run `make` to install js deps
2. `./server.py`
3. open `http://localhost:3000`

