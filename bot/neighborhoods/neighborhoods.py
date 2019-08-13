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


def write_aditional_info(nlu_file):
    nlu_file.write("## lookup:neighborhood\n")
    nlu_file.write("data/lookup/neighborhoods.txt\n\n")
    nlu_file.write("## intent:neighborhood_data\n")


def write_txt_and_md_files(txt_path, md_path, neighborhoods_dict):
    txt_file = open(txt_path, "w+")
    nlu_file = open(md_path, "w+")

    write_aditional_info(nlu_file)

    neighborhoods = []

    for element in neighborhoods_dict:
        neighborhoods.append(element.get("name").lower().strip())

    neighbs_without_duplicates = list(dict.fromkeys(sorted(neighborhoods)))

    for neighborhood in neighbs_without_duplicates:
        txt_file.write("{}\n".format(neighborhood))

        nlu_file.write("- [{}](neighborhood)\n".format(neighborhood))

        # Verifying if neighborhood have accents
        # and writing the possibilities of accentless writing
        try:
            neighborhood.encode('ascii')
        except UnicodeEncodeError:
            txt_file.write("{}\n".format(unidecode.unidecode(neighborhood)))

    txt_file.close()
    nlu_file.close()


if __name__ == "__main__":
    txt_path = "data/lookup/neighborhoods.txt"
    md_path = "data/nlu/neighborhoods.md"

    neighborhoods_dict = get_neighborhoods_from_api()

    write_txt_and_md_files(txt_path, md_path, neighborhoods_dict)
