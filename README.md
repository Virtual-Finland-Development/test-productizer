# test-productizer

A simple test productizer app

## Description

An example environment for setting up a data source for the use of the dataspace-product.

The devenv-setup access points used:

- https://statfin.stat.fi/pxweb/api/v1/en/StatFin/

## Running the app

### Run locally with docker

#### docker compose

- `docker compose up`

#### docker run

- `docker build -t test-productizer .`
- `docker run --rm -it -p 8000:8000 test-productizer`

### Run locally with python

#### Requirements

- python >= 3.10
- python-pip
- make

#### Install

- `make install`

#### Usage

- `make run` # Run the app
- `make dev` # run with hot reload

## Usage:

- After the app running..
- See endpoint documentation: http://localhost:8000/docs

### References

- https://tilastokeskus.fi/ajk/verkkosivu-uudistus/uudistuksen-vaikutukset-statfin-tietokantaan.html

- Dokumentaation: https://statfin.stat.fi/api1.html

Vanhat linkit:

- Tilastokeskuksen avoimet tietokanta-aineistot: https://www.stat.fi/org/avoindata/pxweb.html
- Dokumentaatio: http://pxnet2.stat.fi/api1.html
- API-linkki: https://pxnet2.stat.fi/PXWeb/api/v1/fi/Kuntien_avainluvut/
- Kannan rakenne: [https://pxnet2.stat.fi/PXWeb/api/v1/fi/Kuntien_avainluvut/?query=\*&filter=\*](https://pxnet2.stat.fi/PXWeb/api/v1/fi/Kuntien_avainluvut/?query=*&filter=*)
