import sqlalchemy
from supabase_models import Major
from utils import get_df, get_session


def get_major_mapping():
    session = get_session()
    majors = session.query(Major).all()
    session.close()
    return {major.abbr: major.id for major in majors}


def add_major():
    session = get_session()
    df = get_df()
    df = df[["subject", "subject_descr"]].reset_index(drop=True)
    df = df.drop_duplicates()
    df = df[~df.subject.isin(get_major_mapping().keys())]
    majors = [
        Major(name=row.subject_descr, abbr=row.subject) for _, row in df.iterrows()
    ]

    session.add_all(majors)
    session.commit()
    session.close()


if __name__ == "__main__":
    add_major()
