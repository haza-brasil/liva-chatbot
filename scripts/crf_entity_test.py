import grequests
import json
import logging
import random

logger = logging.getLogger(__name__)

wanna = [
    "quero",
    "gostaria de",
    "tenho interesse em",
    "pretendo",
    "intento",
    "cobiço",
    "almejo",
    "me interesso em"
]

buy = [
    "comprar",
    "compra",
    "obter",
    "adquirir"
]

quantity = [
    "um",
    "uma"
]

property_type = [
    "casa",
    "apartamento",
    "ap",
    "comércio",
    "comercio",
    "loja",
    "estabelecimento",
    "terreno",
    "lote"
]

adverb = [
    "em",
    "aqui em",
    "no",
    "na"
]


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


def split_list(n_list, n):
    return [
        n_list[i * n:(i + 1) * n] for i in range((len(n_list) + n - 1) // n)
    ]


def generate_text(neighborhood):
    return "{} {} {} {} {} {}".format(random.choice(wanna),
                                      random.choice(buy),
                                      random.choice(quantity),
                                      random.choice(property_type),
                                      random.choice(adverb),
                                      neighborhood)


def post_requests(url, neighborhoods):
    for neighborhood in neighborhoods:
        text = generate_text(neighborhood)
        # text = "quero comprar uma casa em {}".format(neighborhood)
        # text = "{}".format(neighborhood)

        yield grequests.post(url, json={"text": text})


def check_for_romans(entities, neighborhood):
    neighborhood_contains_roman = False

    romans = {
        "1": "i",
        "2": "ii",
        "3": "iii",
        "4": "iv",
        "5": "v"
    }

    neigh_with_int = ""

    # "guará i" -> "i"
    roman_number = neighborhood.split()[-1:][0]

    for key, value in romans.items():
        if key == roman_number:
            # "guará 1" -> "guará i"
            neigh_with_int = ' '.join(neighborhood.split(' ')[:-1]) + \
                             ' {}'.format(value)
            break

    if neigh_with_int and neigh_with_int in entities:
        neighborhood_contains_roman = True

    return neighborhood_contains_roman


def send_requests(n_list, neighborhoods_json):
    url = "http://localhost:5005/model/parse"

    generators = []

    for neighborhoods in n_list:
        rs = post_requests(url, neighborhoods)
        generators.append(rs)

    count_hits, count_misses = (0, 0)

    # [[n requests], [n requests], ...]
    for index_list, generator in enumerate(generators):
        for index_neigh, request in enumerate(grequests.map(generator)):
            if request.status_code == 200:
                entities = str(json.loads(request.content).get("entities"))

                neighborhood = n_list[index_list][index_neigh]
                neighborhood = neighborhood.replace(" -", "").replace("'", " ")

                if neighborhood in entities:
                    count_hits += 1
                else:
                    if check_for_romans(entities, neighborhood):
                        count_hits += 1
                    else:
                        text = json.loads(request.content).get("text")
                        logger.warning(
                            "{}\n{}\n".format(text, entities))
                        count_misses += 1

    total = count_hits + count_misses

    try:
        result = (count_hits / total) * 100
    except Exception:
        raise

    f = open("analytics/results.txt", "a+")
    f.write("\nTotal: {} | Acertos: {} | Erros: {}\n".format(
        total, count_hits, count_misses))
    f.write("Porcentagem de acertos: {:.2f}%\n".format(result))
    f.close()


if __name__ == "__main__":
    neighborhoods_path = "bot/data/neighborhoods.txt"
    json_path = "bot/actions/neighborhoods.json"

    f = open(json_path, "r")
    neighborhoods_json = json.load(f)
    f.close()

    neighborhoods = read_file(neighborhoods_path)

    neighborhoods_split_list = split_list(neighborhoods, 1000)

    send_requests(neighborhoods_split_list, neighborhoods_json)
