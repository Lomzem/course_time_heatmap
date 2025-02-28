import json
from models import Model
import logging
import pandas as pd
import datetime
import sys


def main():
    if len(sys.argv) == 1:
        print(f"Usage: {sys.argv[0]} <path_to_json_file>")
        return

    with open(sys.argv[1]) as f:
        data = json.load(f)

    courses = []
    for course in data["classes"]:
        course = Model(**course)
        courses.append(course)

    start_time = pd.Timestamp("07:00:00")
    end_time = pd.Timestamp("18:00:00")
    minute_index = pd.date_range(start_time, end_time, freq="1min").time

    mo_student_counts = pd.Series(0, index=minute_index)
    tu_student_counts = pd.Series(0, index=minute_index)
    we_student_counts = pd.Series(0, index=minute_index)
    th_student_counts = pd.Series(0, index=minute_index)
    fr_student_counts = pd.Series(0, index=minute_index)

    for course in courses:
        start_time = course.meetings[0].start_time
        if start_time == "":
            continue
        end_time = course.meetings[0].end_time

        start_time = datetime.datetime.strptime(start_time, "%H.%M.%S.000000")
        end_time = datetime.datetime.strptime(end_time, "%H.%M.%S.000000")

        for minute in minute_index:
            if start_time.time() <= minute <= end_time.time():
                if "Mo" in course.meetings[0].days:
                    mo_student_counts[minute] += course.enrollment_total
                if "Tu" in course.meetings[0].days:
                    tu_student_counts[minute] += course.enrollment_total
                if "We" in course.meetings[0].days:
                    we_student_counts[minute] += course.enrollment_total
                if "Th" in course.meetings[0].days:
                    th_student_counts[minute] += course.enrollment_total
                if "Fr" in course.meetings[0].days:
                    fr_student_counts[minute] += course.enrollment_total

    mo_student_counts.to_csv("output_csvs/mo_count.csv")
    logging.info("Wrote monday to output_csvs/mo_count.csv")

    tu_student_counts.to_csv("output_csvs/tu_count.csv")
    logging.info("Wrote tuesday to output_csvs/tu_count.csv")

    we_student_counts.to_csv("output_csvs/we_count.csv")
    logging.info("Wrote wednesday to output_csvs/we_count.csv")

    th_student_counts.to_csv("output_csvs/th_count.csv")
    logging.info("Wrote thursday to output_csvs/th_count.csv")

    fr_student_counts.to_csv("output_csvs/fr_count.csv")
    logging.info("Wrote friday to output_csvs/fr_count.csv")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
