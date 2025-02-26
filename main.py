import json
from models import Model


def main():
    with open("out.json") as f:
        data = json.load(f)

    for course in data["classes"]:
        # print(course, "\n\n")
        course = Model(**course)
        print(course)


if __name__ == "__main__":
    main()
