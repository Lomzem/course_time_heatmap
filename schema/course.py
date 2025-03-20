import sqlalchemy
from major import get_major_mapping
from supabase_models import Course
from utils import get_df, get_session


def get_course_mapping():
    db_session = get_session()
    courses = db_session.query(Course).all()
    db_session.close()

    return {f"{c.majorId}{c.catalogNumber}": c.id for c in courses}


def add_course():
    session = get_session()
    df = get_df()

    df = df[["subject", "catalog_nbr"]]
    df = df.drop_duplicates()

    major_map = get_major_mapping()
    df["subjectId"] = df.subject.map(major_map)

    df["compositeKey"] = df.subjectId.astype(str) + "" + df.catalog_nbr.astype(str)

    df = df[~df.compositeKey.isin(get_course_mapping().keys())]

    courses = [
        Course(majorId=row.subjectId, catalogNumber=row.catalog_nbr)
        for _, row in df.iterrows()
    ]

    session.add_all(courses)
    session.commit()
    # for course in courses:
    #     try:
    #         session.add(course)
    #         session.commit()
    #         print(f"Added course {course.id}")
    #     except sqlalchemy.exc.IntegrityError:
    #         session.rollback()
    #         print(f"Duplicate: Skipping Course({course.id})")
    #         continue
    #
    # session.close()
    session.close()


if __name__ == "__main__":
    add_course()
