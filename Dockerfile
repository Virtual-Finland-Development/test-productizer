# build: docker build -t "test-productizer" .
# run: docker run -it --rm -p 8000:8000 test-productizer
FROM python:3.10-slim as base

RUN apt-get update && apt-get install make
RUN python -m pip install --upgrade pip

WORKDIR /app
COPY . .

RUN make install

CMD ["make", "run"]