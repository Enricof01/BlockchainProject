import requests

NODE1URL = "http://127.0.0.1:5001"
NODE2URL = "http://127.0.0.1:5002"

def main():
    """Testing der verschiedenen funktionen"""
    res = requests.get(f"{NODE2URL}/status")
    print(res.json().get("peers"))

    requests.post(f"{NODE2URL}/mine")


    #Transaktionen simulieren



if __name__ == "__main__":
    main()