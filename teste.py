import requests

PUSHY_PAY_TOKEN = "17612|1pNzV0djvXZckRrH1PtdCjU7S2ryY20VRM0G0pYAcab94af6"

def testar_api():
    url = "https://pushypay.com/api/status"
    headers = {"Authorization": f"Bearer {PUSHY_PAY_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        print("STATUS CODE:", response.status_code)
        print("RESPOSTA:", response.text)
    except requests.exceptions.RequestException as e:
        print("Erro ao conectar na API:", e)

testar_api()
