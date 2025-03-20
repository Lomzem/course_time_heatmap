import sqlalchemy
from course import get_course_mapping
from major import get_major_mapping
from supabase_models import Session
from utils import get_df, get_session


def get_session_mapping():
    db_session = get_session()
    sessions = db_session.query(Session).all()
    db_session.close()
    return {f"{s.courseId}{s.termId}{s.sectionCode}": s.id for s in sessions}


def add_session():
    db_session = get_session()
    df = get_df()
    df = df[["termId", "sectionCode", "instruction_mode", "subject", "catalog_nbr"]]

    df["subjectId"] = df.subject.map(get_major_mapping())
    df["courseIdCompositeKey"] = df.subjectId.astype(str) + "" + df.catalog_nbr.astype(str)
    df["courseId"] = df.courseIdCompositeKey.map(get_course_mapping())

    df.sectionCode = df.sectionCode.astype(int)

    df = df.drop_duplicates()
    df["compositeKey"] = (
        df.courseId.astype(str) + df.termId.astype(str) + df.sectionCode.astype(str)
    )
    df = df[~df.compositeKey.isin(get_session_mapping().keys())]

    sessions = [
        Session(
            courseId=row.courseId,
            termId=row.termId,
            sectionCode=row.sectionCode,
            instructionMode=row.instruction_mode,
        )
        for _, row in df.iterrows()
    ]

    db_session.add_all(sessions)
    db_session.commit()

    # for session in sessions:
    #     try:
    #         db_session.add(session)
    #         db_session.commit()
    #         print(f"Added session {session.courseId}")
    #     except sqlalchemy.exc.IntegrityError:
    #         db_session.rollback()
    #         print(f"Duplicate: Skipping Session({session.courseId})")
    #         continue

    # for session in sessions:
    #     try:
    #         session.add(session)
    #         session.commit()
    #         print(f"Added session {session.courseId}")
    #     except sqlalchemy.exc.IntegrityError:
    #         session.rollback()
    #         print(f"Duplicate: Skipping Session({session.courseId})")
    #         continue
    #
    # print(df)
    # session.close()


if __name__ == "__main__":
    add_session()
