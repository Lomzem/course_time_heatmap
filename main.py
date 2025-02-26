import json


def main():
    with open("out.json") as f:
        data = json.load(f)

    print(data)


if __name__ == "__main__":
    main()
