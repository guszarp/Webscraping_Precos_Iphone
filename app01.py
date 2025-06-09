import requests

def fetch_page(url):
    response = requests.get(url)
    print(response.text)

if __name__ == "__main__":
    url = "https://www.mercadolivre.com.br/apple-iphone-16-pro-1-tb-titnio-preto-distribuidor-autorizado/p/MLB1040287851#polycard_client=search-nordic&wid=MLB5054621110&sid=search&searchVariation=MLB1040287851&p"
    page_content = fetch_page()
    print(page_content)