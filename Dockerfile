# build: docker build -t "testbed-test-productizer" .
# run: docker run -it --rm -p 8000:8000 testbed-test-productizer
FROM python:3.10-slim as base

RUN apt-get update && apt-get install make xmlsec1
RUN python -m pip install --upgrade pip

WORKDIR /app
COPY . .

RUN make install

CMD ["make", "run"]