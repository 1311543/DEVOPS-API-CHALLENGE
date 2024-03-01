#!/bin/bash

alembic stamp head
alembic revision --autogenerate -m "Sync schema Migration"
alembic current
alembic upgrade head