import tweepy
import time
import db
import os

consumer_key = 'COLOQUE A CONSUMER KEY AQUI'
consumer_secret = 'COLOQUE O CONSUMER SECRET AQUI'
token_key = 'COLOQUE A TOKEN KEY AQUI'
token_secret = 'COLOQUE O TOKEN SECRET AQUI'

def download_tweets(id_file, sentiment, last_id_file=None):
    with open(id_file) as infile:
        # Começa pelo último tweet pesquisado 
        # (salvo em um arquivo local)
        if os.path.isfile(last_id_file):
            print("Começando de onde você parou...")

            with open(last_id_file) as f:
                last_id = f.read().strip()
                print(f"Começando com ID {last_id}...")

            for tweet_id in infile:
                tweet_id = tweet_id.strip()
                print(tweet_id)
                if tweet_id == last_id:
                    break
            else: # se percorreu o arquivo inteiro e não achou o ID
                print(f"Finalizado com arquivo {id_file}")
                return

        # Inicializa uma lista de IDs para realizar um request
        ids = []

        # Adquire tweets do arquivo
        for tweet_id in infile:
            tweet_id = tweet_id.strip()

            # Apenas prossegue quando a lista tiver 100 elementos
            # (100 é o limite do método statuses_lookup)
            if len(ids) < 100:
                ids.append(tweet_id)
                continue

            # Tenta obter 100 tweets
            # (obtém menos já que alguns não estarão disponíveis)
            tweets=[]
            try:
                tweets = api.statuses_lookup(ids)
                print(f"Obtidos {len(tweets)} tweets")
            except tweepy.error.TweepError as e:
                s = e.__str__()
                print("xxxxxxxxxx")
                print("Erro na API! Códigos:")
                print(s)
                if "rate limit exceeded" in s.lower():
                    print("Batemos no limite da API. Esperando 15 mins...")
                    time.sleep(15*60)
                    download_tweets(id_file, sentiment, last_id_file)
                    break
                print("xxxxxxxxxx")

            # Insere os tweets na database
            for tweet in tweets:
                if db.exist_tweet(str(tweet.id)):
                    print("x-- tweet com id: ", tweet.id,
                          "já foi capturado --x")
                    continue

                db.add_tweet(tweet, sentiment)
                print("*--tweet com id: ", tweet.id, "capturado --*")

            # Salva o último ID utilizado
            if last_id_file:
                with open(last_id_file, 'w') as f:
                    f.write(ids[-1])

            # Reinicia o vetor de acúmulo de IDs
            ids = []


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(token_key, token_secret)
api = tweepy.API(auth)

LAST_ID_FILE = os.path.join(
    (os.path.dirname(os.path.realpath(__file__))),
    ".last_id"
)

print("Capturando tweets positivos ...")
download_tweets("positivos.txt", 1,
                last_id_file=LAST_ID_FILE)

print("Capturando tweets negativos ...")
download_tweets("negativos.txt", 0,
                last_id_file=LAST_ID_FILE)

print("Fim.")
