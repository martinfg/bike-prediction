import requests
import click
from tqdm import tqdm

@click.command()
@click.argument('data-from', type=click.INT)
@click.argument('api-url', type=click.STRING)
def main(data_from, api_url):

    print("fetching latest data from server")
    result = []

    # get inital rows to determine size of data to be loaded
    url = api_url + f'/bikes/{data_from}'
    resp = requests.get(url=url)
    data = resp.json()
    result.append(data["rows"])

    # get rest of data
    with tqdm(total=data["remaining"]) as pbar:
        next_page = data["next"]
        while True:
            url = api_url + next_page
            # print("url:", url)
            # print("\rremaining rows:", data["remaining"], end="")
            resp = requests.get(url=url)
            data = resp.json()
            result.append(data["rows"])
            pbar.update(5)
            if data["next"] != "":
                next_page = data["next"]
            else:
                break

if __name__ == "__main__":
    main()