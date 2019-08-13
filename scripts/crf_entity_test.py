import grequests
import json


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


def post_requests(url, bairros):
    for bairro in bairros:
        text = "quero comprar uma casa em {}".format(bairro)
        # text = "{}".format(bairro)

        yield grequests.post(url, json={"text": text})


def send_requests(n_list):
    url = "http://localhost:5005/model/parse"

    generators = []

    for neighborhoods in n_list:
        rs = post_requests(url, neighborhoods)
        generators.append(rs)

    bairro_index = 0
    bairro_count = 0
    count_erros = 0
    count_acertos = 0

    count_one = 0
    count_two = 0
    count_three = 0
    count_four = 0
    cout_five_more = 0

    for generator in generators:
        for request in grequests.map(generator):
            if request.status_code == 200:
                entities = str(json.loads(request.content).get("entities"))

                if n_list[bairro_index][bairro_count] in entities:
                    count_acertos += 1
                else:
                    size = len(n_list[bairro_index][bairro_count].split())

                    if size == 1:
                        count_one += 1
                    elif size == 2:
                        count_two += 1
                    elif size == 3:
                        count_three += 1
                    elif size == 4:
                        count_four += 1
                    elif size > 4:
                        cout_five_more += 1

                    # print(n_list[bairro_index][bairro_count])
                    # print(str(json.loads(request.content).get("entities")))
                    # print('\n')
                    count_erros += 1

                bairro_count += 1

        bairro_index += 1
        bairro_count = 0

    total = count_acertos + count_erros

    try:
        result = (count_acertos / total) * 100
    except Exception:
        print(vars(Exception))

    f = open("results.txt", "a")
    f.write("\nTotal: {} | Acertos: {} | Erros: {}\n".format(total, count_acertos, count_erros))
    f.write("Porcentagem de acertos: {:.2f}%\n".format(result))
    f.write("1: {} | {:.2f}%\n".format(count_one, (count_one / count_erros) * 100))
    f.write("2: {} | {:.2f}%\n".format(count_two, (count_two / count_erros) * 100))
    f.write("3: {} | {:.2f}%\n".format(count_three, (count_three / count_erros) * 100))
    f.write("4: {} | {:.2f}%\n".format(count_four, (count_four / count_erros) * 100))
    f.write("> 4: {} | {:.2f}%\n".format(cout_five_more, (cout_five_more / count_erros) * 100))
    f.close()


if __name__ == "__main__":
    neighborhoods_path = "../bot/data/lookup/neighborhoods.txt"

    neighborhoods = read_file(neighborhoods_path)

    neighborhoods_split_list = split_list(neighborhoods, 1000)

    send_requests(neighborhoods_split_list)
