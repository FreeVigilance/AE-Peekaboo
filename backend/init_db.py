import uuid
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import Boolean, Column, Date, ForeignKey, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.infrastructure.models.public import Drug, SubmissionRule, User
from src.settings import settings


def convert_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def load_csv_to_db(csv_path, db_url):
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user = User(
            id=str(uuid.uuid4()),
            email="admin@admin.com",
            password="$2b$12$V1VeVWlbbb4EesFuaSH.aOj/6u/N4NveGxQFZPWd.5AREevYNIkwq",
            is_admin=True,
        )
        session.add(user)
        session.commit()
    except IntegrityError:
        session.rollback()

    try:
        df = pd.read_csv(csv_path, sep=";")
        df = df.replace(np.nan, None)
        for _, row in df.iterrows():

            drug = Drug(
                id=uuid.UUID(row["drugs.id"]),
                trade_name=row["drugs.trade_name"].replace('®', '') if row["drugs.trade_name"] else "",
                inn=row["drugs.inn"].replace('®', '') if row["drugs.inn"] else "",
                obligation=row["drugs.obligation"],
                release_forms=row["drugs.release_forms"],
            )

            submission_rule = SubmissionRule(
                id=uuid.UUID(row["submission_rules.id"]),
                routename=uuid.UUID(row["submission_rules.routename"]),
                source_countries=row["submission_rules.source_countries"],
                receiver=row["submission_rules.receiver"],
                deadline_to_submit=None,
                format=row["submission_rules.format"],
                other_procedures=row["submission_rules.other_procedures"],
                type_of_event=row["submission_rules.type_of_event"],
            )

            session.add(drug)
            session.add(submission_rule)

            if len(session.new) > 100:
                session.commit()

        session.commit()
        print("Данные успешно загружены в базу данных")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        session.rollback()

    finally:
        session.close()


if __name__ == "__main__":
    CSV_PATH = "./assets/df_for_psql.csv"
    db = settings.db.connection_string.replace("+asyncpg", "")
    load_csv_to_db(CSV_PATH, db)
