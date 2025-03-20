from course import add_course
from major import add_major
from occupancy import add_occupancy
from session import add_session
from weekday import add_weekday


def main():
    add_weekday()
    add_major()
    add_course()
    add_session()
    add_occupancy()


if __name__ == "__main__":
    main()
