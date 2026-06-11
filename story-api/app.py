import os
import json
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


@app.get("/health")
def health():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        now = cur.fetchone()[0]
        cur.close()
        conn.close()

        return jsonify({
            "status": "healthy",
            "database": "connected",
            "time": str(now)
        })

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500


@app.post("/save-result")
def save_result():
    payload = request.get_json(force=True)

    story_id = payload.get("story_id")
    stage = payload.get("stage")
    data = payload.get("data")

    if not story_id or not stage or data is None:
        return jsonify({
            "status": "error",
            "message": "story_id, stage, and data are required"
        }), 400

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO story_pipeline_results (story_id, stage, data)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,
            (story_id, stage, json.dumps(data))
        )

        result_id = cur.fetchone()[0]
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "status": "saved",
            "id": result_id,
            "story_id": story_id,
            "stage": stage
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.get("/result/<story_id>/<stage>")
def get_result(story_id, stage):
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, data, created_at
            FROM story_pipeline_results
            WHERE story_id = %s AND stage = %s
            ORDER BY created_at DESC
            LIMIT 1;
            """,
            (story_id, stage)
        )

        row = cur.fetchone()

        cur.close()
        conn.close()

        if row is None:
            return jsonify({
                "status": "not_found",
                "story_id": story_id,
                "stage": stage
            }), 404

        return jsonify({
            "status": "found",
            "id": row[0],
            "story_id": story_id,
            "stage": stage,
            "data": row[1],
            "created_at": str(row[2])
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.post("/echo")
def echo():
    return request.get_json()
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)