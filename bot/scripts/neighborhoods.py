import json
import os
import requests
import unidecode

LIVA_API_NEIGHBORHOODS = os.getenv('LIVA_API_NEIGHBORHOODS', None)


def get_neighborhoods_from_api():
    url = LIVA_API_NEIGHBORHOODS

    try:
        request = requests.get(url)
    except Exception:
        raise

    neighborhoods_dict = {}

    if request.status_code == 200:
        neighborhoods_dict = json.loads(request.content)
    else:
        print(request.status_code)

    return neighborhoods_dict


def read_file(filepath):
    neighborhoods = []

    with open(filepath) as fp:
        line = fp.readline()
        cnt = 1

        while line:
            neighborhoods.append(line.strip('\n'))

            line = fp.readline()
            cnt += 1

    return neighborhoods


def write_intent_info(nlu_file):
    nlu_file.write("## lookup:neighborhood\n")
    nlu_file.write("data/neighborhoods.txt\n\n")
    nlu_file.write("## intent:neighborhood_data\n")


def treat_romans_and_accents(txt_file, nlu_file, neighborhood):
    romans = {
        "i": "1",
        "ii": "2",
        "iii": "3",
        "iv": "4",
        "v": "5"
    }

    neigh_with_int = ""

    # "guará i" -> "i"
    roman_number = neighborhood.split()[-1:][0]

    for key, value in romans.items():
        if key == roman_number:
            # "guará i" -> "guará 1"
            neigh_with_int = ' '.join(neighborhood.split(' ')[:-1]) + \
                             ' {}'.format(value)
            break

    if neigh_with_int:
        txt_file.write("{}\n".format(neigh_with_int))
        nlu_file.write(
            "- [{}](neighborhood:{})\n".format(neigh_with_int,
                                               neighborhood))

    try:
        neighborhood.encode('ascii')
    except UnicodeEncodeError:
        txt_file.write("{}\n".format(unidecode.unidecode(neighborhood)))

        if neigh_with_int:
            txt_file.write("{}\n".format(unidecode.unidecode(neigh_with_int)))


def write_neighborhood_files(txt_path, md_path,
                             json_path, neighborhoods_dict):
    txt_file = open(txt_path, "w+")
    nlu_file = open(md_path, "w+")

    write_intent_info(nlu_file)

    neighborhoods = []

    neighborhoods_data = {}

    for element in neighborhoods_dict:
        name = element.get("name").strip().lower()

        neighborhoods.append(name)

        clean_name = unidecode.unidecode(
            name.replace(" -", "").replace("'", " "))

        r_name = element.get("representative_name")

        data = {
            "name": r_name.split(", ")[0],
            "uf_code": r_name.split(" - ")[-1],
            "city": " ".join(r_name.split(", ")[1].split(" - ")[:1])
        }

        try:
            neighborhoods_data[clean_name].append(data)
        except KeyError:
            neighborhoods_data[clean_name] = []
            neighborhoods_data[clean_name].append(data)

    json_file = open(json_path, "w+")
    json.dump(neighborhoods_data, json_file, indent=4, ensure_ascii=False)
    json_file.close()

    neighbs_without_duplicates = list(dict.fromkeys(sorted(neighborhoods)))

    for neighborhood in neighbs_without_duplicates:
        txt_file.write("{}\n".format(neighborhood))

        nlu_file.write("- [{}](neighborhood)\n".format(neighborhood))

        treat_romans_and_accents(txt_file, nlu_file, neighborhood)

    txt_file.close()
    nlu_file.close()


if __name__ == "__main__":
    txt_path = "data/neighborhoods.txt"
    md_path = "data/nlu/neighborhoods.md"
    json_path = "actions/neighborhoods.json"

    neighborhoods_dict = get_neighborhoods_from_api()

    write_neighborhood_files(txt_path, md_path, json_path, neighborhoods_dict)

    print("All neighborhoods files created")
