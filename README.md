Opsætning:

1. `docker-compose up --build -d`
2. Hop på http://localhost:1337 og skriv noget til /predict

Hvis du vil træne:

1. Hent glove.6B.zip på https://nlp.stanford.edu/projects/glove/
2. Smid glove.6B.100d.txt ind i `app/datasets/` (den var for stor til at have i git)
3. `docker-compose exec -it active-learning bash`
4. `python models/text_classifier.py` (eller en ny model)

Vi bruger GloVe's pre-trained embeddings til at skabe en matrix af ord værdier

Det er et eller andet smart med afstanden mellem ord... Spørg en matematiker, jeg er her bare
