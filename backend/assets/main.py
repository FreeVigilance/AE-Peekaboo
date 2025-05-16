import uuid
from datetime import datetime

import pandas as pd

df = pd.read_csv("medicines_processed.csv", sep=";")


def convert_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        parsed_date = datetime.strptime(date_str, "%d.%m.%Y")
        return parsed_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None


result = []

for _, row in df.iterrows():
    drug_id = str(uuid.uuid4())
    submission_id = str(uuid.uuid4())

    record = {
        "drugs.id": drug_id,
        "drugs.trade_name": row[
            "Торговое наименование лекарственного препарата"
        ]
        or "",
        "drugs.inn": row[
            "Международное непатентованное или химическое наименование"
        ]
        or "",
        "drugs.obligation": None,
        "drugs.release_forms": row["Формы выпуска"],
        "submission_rules.id": submission_id,
        "submission_rules.routename": drug_id,
        "submission_rules.source_countries": row[
            "Юридическое лицо, на имя которого выдано регистрационное удостоверение (Страна)"
        ],
        "submission_rules.receiver": row[
            "Юридическое лицо, на имя которого выдано регистрационное удостоверение"
        ],
        "submission_rules.deadline_to_submit": convert_date(
            row["Дата регистрации"]
        ),
        "submission_rules.format": None,
        "submission_rules.other_procedures": None,
        "submission_rules.type_of_event": None,
    }
    result.append(record)

result_df = pd.DataFrame(result)
result_df[["drugs.trade_name", "drugs.inn"]].fillna("", inplace=True)

result_df.to_csv("df_for_psql.csv", sep=";")
