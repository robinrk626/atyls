# atyls

# install dependencies using this command
pip install -r requirements.txt


### then run the server using
`uvicorn app:app --reload`


Run the api with following curl

---
curl --location 'localhost:8000/scrape' \
--header 'Authorization: atlysdentalstall' \
--header 'Content-Type: application/json' \
--data '{
    "maxPages": 1


}'
---

