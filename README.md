# Opsætning

## Basic

1. `docker-compose up --build -d`
2. Hop på http://localhost:1337 og skriv noget til /predict

## Hvis du vil træne en model

1. Hent glove.6B.zip på https://nlp.stanford.edu/projects/glove/
2. Smid glove.6B.100d.txt ind i `app/datasets/` (den var for stor til at have i git)
3. `docker-compose exec -it active-learning bash`
4. `python models/text_classifier.py` (eller en ny model)

Vi bruger GloVe's pre-trained embeddings til at skabe en matrix af ord værdier

Det er et eller andet smart med afstanden mellem ord... Spørg en matematiker, jeg er her bare

## Skab kunstig data med Llama (Ollama)

1. `curl -fsSL https://ollama.com/install.sh | sh`
2. `ollama pull llama3.2:3b`
3. `ollama run llama3.2:3b`
4. _skriv prompt_
5. $$$ profit

Alternativt kan vi gøre det programmelt med: https://huggingface.co/meta-llama/Llama-3.2-3B

## Til når vi skal involvere Datascanner

1. Smid data ind her: os2datascanner/dev-environment/data/<'ny folder'>
2. `docker-compose exec admin django-admin quickstart_dev`
3. Log på Datascanner http://localhost:8020
4. Ret filscan-jobbet til kun at kigge på den nye folder
5. Find ud af hvor vi hooker Datascanner på http://localhost:1337/predict og /train
