### Setup

```shell
brew install pyenv
```

```shell
make setup
```

### Install dependencies

```shell
poetry install
source .venv/bin/activate
```

### Run database

```shell
docker compose up
```

### Install spacy model

```shell
python3 -m spacy download ru_core_news_sm
```

### Run app
```shell
python3 -m uvicorn src.interfaces.api.app:app --loop uvloop --reload
```

### Make migrations

```shell
alembic revision --autogenerate -m "<Название>"
```

### Apply migrations

```shell
alembic upgrade head
```
