import requests
from flask import Flask, render_template, request

app = Flask(__name__)
TMDB_API_KEY = "df6813769a1011b240f983195d0c2cd1"
TMDB_BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w200"

def tmdb_id_from_movie(name):
    url = f"{TMDB_BASE}/search/movie"
    resp = requests.get(url, params={"api_key": TMDB_API_KEY, "query": name}).json()
    results = resp.get("results", [])
    if results:
        return results[0]["id"], results[0]["title"], results[0].get("poster_path")
    return None, None, None

def get_movie_cast(movie_id):
    url = f"{TMDB_BASE}/movie/{movie_id}/credits"
    resp = requests.get(url, params={"api_key": TMDB_API_KEY}).json()
    return [(c["id"], c["name"], c.get("profile_path")) for c in resp.get("cast", [])]

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        movie_a_name = request.form["movie_a"]
        movie_list_raw = request.form["movie_list"]
        movie_list = [m.strip() for m in movie_list_raw.split(",")]

        movie_a_id, movie_a_title, _ = tmdb_id_from_movie(movie_a_name)
        if not movie_a_id:
            results.append({"error": f"Movie '{movie_a_name}' not found"})
        else:
            cast_a = get_movie_cast(movie_a_id)
            cast_a_ids = {c[0]: c for c in cast_a}

            for m_name in movie_list:
                movie_b_id, movie_b_title, poster_path = tmdb_id_from_movie(m_name)
                if not movie_b_id:
                    continue
                cast_b = get_movie_cast(movie_b_id)
                for actor_id, actor_name, headshot_path in cast_b:
                    if actor_id in cast_a_ids:
                        results.append({
                            "movie_b_title": movie_b_title,
                            "movie_b_poster": IMAGE_BASE+poster_path if poster_path else "",
                            "actor_name": actor_name,
                            "actor_headshot": IMAGE_BASE+headshot_path if headshot_path else ""
                        })
                        break
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
