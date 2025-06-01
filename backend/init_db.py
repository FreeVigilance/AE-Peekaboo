import uuid
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import Boolean, Column, Date, ForeignKey, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.infrastructure.models.public import Drug, SubmissionRule, SubmissionRuleDrug, User
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

    # Словари для отслеживания уже добавленных записей
    added_drugs = {}
    added_submission_rules = {}

    try:
        # Создаем админ пользователя
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
            drug_id = uuid.UUID(row["drugs.id"])
            submission_rule_id = uuid.UUID(row["submission_rules.id"])

            if drug_id not in added_drugs:
                drug = Drug(
                    id=drug_id,
                    trade_name=row["drugs.trade_name"] or "",
                    inn=row["drugs.inn"] or "",
                    obligation=row["drugs.obligation"],
                    release_forms=row["drugs.release_forms"],
                )
                session.add(drug)
                added_drugs[drug_id] = drug

            if submission_rule_id not in added_submission_rules:
                submission_rule = SubmissionRule(
                    id=submission_rule_id,
                    # Убираем routename, так как его больше нет в модели
                    source_countries=row["submission_rules.source_countries"],
                    receiver=row["submission_rules.receiver"],
                    deadline_to_submit=None,
                    format=row["submission_rules.format"],
                    other_procedures=row["submission_rules.other_procedures"],
                    type_of_event=row["submission_rules.type_of_event"] if pd.notna(
                        row["submission_rules.type_of_event"]) else None,
                )
                session.add(submission_rule)
                added_submission_rules[submission_rule_id] = submission_rule

            # Создаем связь в промежуточной таблице
            try:
                # Проверяем, не существует ли уже такая связь
                existing_link = session.query(SubmissionRuleDrug).filter_by(
                    submission_rule_id=submission_rule_id,
                    drug_id=drug_id
                ).first()

                if not existing_link:
                    submission_rule_drug = SubmissionRuleDrug(
                        submission_rule_id=submission_rule_id,
                        drug_id=drug_id
                    )
                    session.add(submission_rule_drug)
            except Exception as e:
                print(f"Ошибка при создании связи между {drug_id} и {submission_rule_id}: {e}")
                continue

            # Периодически коммитим для избежания проблем с памятью
            if len(session.new) > 100:
                session.commit()

        session.commit()
        print("Данные успешно загружены в базу данных")
        print(f"Добавлено лекарств: {len(added_drugs)}")
        print(f"Добавлено правил подачи: {len(added_submission_rules)}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        session.rollback()

    finally:
        session.close()


if __name__ == "__main__":
    CSV_PATH = "./assets/df_for_psql.csv"
    db = settings.db.connection_string.replace("+asyncpg", "")
    load_csv_to_db(CSV_PATH, db)