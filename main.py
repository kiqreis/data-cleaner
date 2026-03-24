from faker import Faker
from unidecode import unidecode
import pandas as pd
import random


fake = Faker("pt_BR")


data = [
    {
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Salary": round(random.uniform(1_621, 50_000), 2),
        "Occupation": fake.job(),
        "Email": fake.free_email(),
        "PhoneNumber": fake.phone_number(),
        "Address": fake.address().replace("\n", ", "),
        "DateOfBirth": fake.date_of_birth(minimum_age=18, maximum_age=65),
    }
    for _ in range(1_000)
]


with open("data.csv", "w+", encoding="utf-8") as f:
    df = pd.DataFrame(data)
    df.to_csv("data.csv", index=False)


def load_and_clean(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    df = (
        df.pipe(normalize_column_names)
        .pipe(strip_str)
        .pipe(drop_duplicates)
        .pipe(coerce_numeric_columns)
    )

    return df


def main():
    df = load_and_clean("data.csv")

    print(df.head(n=20))


if __name__ == "__main__":
    main()
