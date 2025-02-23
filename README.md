```markdown
# OC_IA_P10_RecoFunction

Ce dépôt contient la **fonction Azure** permettant de déployer le moteur de recommandation d’articles en mode _serverless_. L’objectif est d’exposer une **API REST** qui, pour un `user_id` donné, renvoie une liste d’articles recommandés.

---

## Architecture et fonctionnement

- **Alternating Least Squares (ALS)** : Le modèle de recommandation (entraîné au préalable) est chargé au démarrage de la fonction Azure.  
- **Azure Blob Storage** : Les données d’interactions (fichier `clicks_sample.csv`) ainsi que les fichiers `.npz` (matrice de popularité, modèle ALS) sont stockés sur Azure Blob Storage.  
- **API REST** : La fonction `recommend_articles/__init__.py` est déclenchée via une requête HTTP. Elle lit les données dans le Blob Storage, exécute l’algorithme ALS et retourne la liste des articles recommandés.

Cette architecture fait partie d’un **écosystème serverless** :

1. **[OC_IA_P10_Recommandation_contenu](https://github.com/preudh/OC_IA_P10_Recommandation_contenu)** : Contient le Notebook permettant d’entraîner et de tester le modèle ALS (filtrage collaboratif).  
2. **OC_IA_P10_RecoFunction (ce dépôt)** : Héberge l’API de recommandation, déployée sur Azure Functions.  
3. **[OC_IA_P10_STREAMLIT_APP](https://github.com/preudh/OC_IA_P10_STREAMLIT_APP)** : Fournit une application Streamlit pour l’interface utilisateur, accessible ici : [https://p10-streamlit-app-2025.azurewebsites.net/](https://p10-streamlit-app-2025.azurewebsites.net/).

Lorsque l’utilisateur sur l’interface Streamlit sélectionne un `user_id`, un appel `GET` est envoyé à l’API Azure Functions (hébergée dans ce dépôt), qui renvoie alors la recommandation.

---

## Installation et exécution (en local)

1. **Cloner le dépôt**  
   ```bash
   git clone https://github.com/preudh/OC_IA_P10_RecoFunction.git
   ```

2. **Installer les dépendances** (dans un environnement virtuel, recommandé)  
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer Azure Functions localement**  
   - Installer [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local?tabs=v2) **ou** utiliser **Visual Studio Code** avec l’extension **Azure Functions** pour un démarrage simplifié.  
   - Vérifier que vous disposez d’un compte Azure Blob Storage et que les variables d’environnement nécessaires (`AZURE_STORAGE_ACCOUNT`, etc.) sont correctement définies (dans `.env` ou via vos paramètres d’environnement).  

4. **Démarrer la fonction Azure**  
   - Avec **Visual Studio Code** et l’extension **Azure Functions**, ouvrir le projet et cliquer sur “Run” dans l’interface.  
   - Ou bien exécuter manuellement (après installation des Core Tools) :  
     ```bash
     func start
     ```
   La fonction sera disponible sur `http://localhost:7071/`.

---

## Déploiement sur Azure

- **Visual Studio Code** est fortement recommandé pour déployer vos Azure Functions. Les **extensions natives** (ex. _Azure Tools_, _Azure Functions_) facilitent :  
  - l’authentification à votre abonnement Azure,  
  - la création d’une Function App,  
  - le déploiement continu (CI/CD) via GitHub Actions ou Azure DevOps.

### Étapes générales

1. **Se connecter à Azure** via l’extension dans Visual Studio Code.  
2. **Créer une Function App** sur Azure (ou en sélectionner une existante).  
3. **Déployer** directement à partir de Visual Studio Code (“Deploy to Function App”).  
4. **Configurer les variables d’environnement** (ex. `AZURE_STORAGE_ACCOUNT`) dans les **Application Settings** de votre Function App.  
5. **Tester** l’URL publique de la fonction (ex. `https://<votre-fonction>.azurewebsites.net/api/recommend_articles`) pour vérifier qu’elle retourne bien des recommandations.

---

## Points clés

- **Mise à l’échelle automatique** : Azure Functions ne tourne qu’en réponse à des requêtes, ce qui réduit les coûts et facilite la montée en charge.  
- **Simplicité de maintenance** : Vous ne gérez pas de serveurs (serverless).  
- **Interaction directe** : L’application Streamlit ([lien](https://p10-streamlit-app-2025.azurewebsites.net/)) envoie les paramètres `user_id` à cette fonction, qui renvoie la liste d’articles recommandés au format JSON.

