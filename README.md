# Personal finance dashboard

## Support for banks and statement

| Bank                | statement type | format |
| ------------------- | -------------- | ------ |
| State Bank Of India | SB, PPF, Loan  | csv    |
| Canara Bank         | SB             | csv    |
| ICICI Bank          | SB             | xls    |
| PhonePe             | UPI            | pdf    |

## Running

### Docker

```
$ make docker_build
$ docker run -it --rm -p 8080:8080 pf_dashboard:latest
```

And then open `http://localhost:8080/pf/` in browser


### Manual

```
$ make init
$ make install
$ . venv/bin/activate
$ ./server.py
```
And then open `http://localhost:3000/` in browser

### Testing

```
$ make init
$ make test
```