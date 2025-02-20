import azure.functions as func
import logging
import os
import json
import numpy as np
import implicit
from scipy.sparse import csr_matrix

# Import local (vous venez de renommer 'azure_functions' en 'shared')
from shared.azure_blob import load_clicks_csv

os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

CSR_FILE = "csr_article_popularity.npz"
ALS_FILE = "als_implicit_model.npz"

# Chargement du modèle ALS
csr_data = np.load(CSR_FILE)
csr_article_popularity = csr_matrix((csr_data["data"], csr_data["indices"], csr_data["indptr"]),
                                    shape=csr_data["shape"])
als_model = implicit.als.AlternatingLeastSquares()
als_model = als_model.load(ALS_FILE)

def recommend_collaborative_articles(user_id: int, top_k: int = 5):
    article_ids, scores = als_model.recommend(
        user_id,
        csr_article_popularity[user_id],
        N=top_k,
        filter_already_liked_items=True
    )
    return article_ids

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Azure Function - ALS Recommender triggered")

    user_id_str = req.params.get("user_id")
    if not user_id_str:
        try:
            req_body = req.get_json()
            user_id_str = req_body.get("user_id")
        except ValueError:
            pass

    if not user_id_str:
        return func.HttpResponse(
            "Missing parameter: user_id",
            status_code=400
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        return func.HttpResponse(
            "Invalid user_id. Must be an integer.",
            status_code=400
        )

    if user_id < 0 or user_id >= csr_article_popularity.shape[0]:
        return func.HttpResponse(
            f"User ID {user_id} is out of range.",
            status_code=400
        )

    try:
        # On récupère le CSV depuis Azure Blob
        clicks_df = load_clicks_csv()
        user_clicks = clicks_df[clicks_df["user_id"] == user_id]
        if user_clicks.empty:
            logging.info(f"No explicit clicks for user_id={user_id}.")
        else:
            logging.info(f"User {user_id} found with {len(user_clicks)} interactions.")
    except Exception as ex_csv:
        logging.error(f"Error loading CSV from Blob: {ex_csv}")

    try:
        recommended_articles = recommend_collaborative_articles(user_id)
    except Exception as exc:
        logging.error(f"Error in ALS recommend: {exc}")
        return func.HttpResponse(
            f"Server error: {str(exc)}",
            status_code=500
        )

    return func.HttpResponse(
        json.dumps(recommended_articles.tolist()),
        status_code=200,
        mimetype="application/json"
    )


