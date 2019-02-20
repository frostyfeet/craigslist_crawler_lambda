from search_master import SearchMaster
import requests
import bs4

class Craiglist(SearchMaster):
    def __init__(self, urls, s3_filename, slack_token):
        super().__init__(urls, s3_filename, slack_token)

    def pull_results(self, urls):
        results = []
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                html = bs4.BeautifulSoup(response.content, 'html.parser')
                iltags = html.find('ul', {'class': 'rows'}).findAll('li')
                for il in iltags:
                    id = il.find('a', {'class': 'result-title hdrlnk'}).get('data-id') 
                    href = il.find('a', {'class': 'result-title hdrlnk'}).get('href')
                    results.append({
                        "id": id,
                        "url": href
                    })
            except requests.exceptions.HTTPError as e:
                print("Error getting URL")
            except Exception as e:
                print("Error parsing {}".format(e))
        return results


        
def handler(event, context):
    urls = [
        "https://vancouver.craigslist.org/search/sss?query=travel+crib+bjorn&sort=rel&search_distance=5&postal=V6K3J3&max_price=160",
        "https://vancouver.craigslist.org/search/sss?query=travel+crib+guava&sort=rel&search_distance=8&postal=V6K3J3&max_price=150"
    ]

    client = Craiglist(urls, "cribs.pickle", "")
    current_results = client.pull_results(urls)
    # Check if there are any results
    if current_results:
        new_results = client.get_new_results(current_results)
        if new_results:
            print("Found new results: {}".format(len(new_results)))
            for result in new_results:
                print("Sending info to slack")
                client.send_slack(result['url'])
            client.add_new_results(new_results)
            print("Writing file to s3")
            client.write_s3_file()
        else: 
            print("No new results")
    else: 
        print("0 results found")

