import sqlalchemy
from major import get_major_mapping
from supabase_models import Course
from utils import get_df, get_session


def add_course():
    session = get_session()
    df = get_df()
    df.courseId = df.courseId.astype(int)
    df = df[["courseId", "subject"]]
    df = df.drop_duplicates()
    major_map = get_major_mapping()
    df["subjectId"] = df.subject.map(major_map)

    ids = [r[0] for r in session.query(Course.id).all()]
    df = df[~df.courseId.isin(ids)]

    courses = [
        Course(id=row.courseId, majorId=row.subjectId) for _, row in df.iterrows()
    ]

    for course in courses:
        try:
            session.add(course)
            session.commit()
            print(f"Added course {course.id}")
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            print(f"Duplicate: Skipping Course({course.id})")
            continue

    session.close()


if __name__ == "__main__":
    add_course()
