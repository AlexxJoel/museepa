import json

import psycopg2


def lambda_handler(event, _context):
    conn = None
    cur = None
    try:
        # Conexión a la base de datos
        conn = psycopg2.connect(
            host="ep-gentle-mode-a4hjun6w-pooler.us-east-1.aws.neon.tech",
            user="default",
            password="pnQI1h7sNfFK",
            database="verceldb",
        )

        # check if the connection is successful
        if conn is None:
            return {
                "statusCode": 500,
                "body": json.dumps("Connection to the database failed"),
            }

        # Check if the event has a body
        if "body" not in event:
            return {"statusCode": 400, "body": json.dumps("No body provided")}

        # Try to load the JSON body from the event
        try:
            request_body = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "The request body is not valid JSON"}),
            }

        # todo: validate the request body

        request_body = json.loads(event["body"])

        id = request_body["id"]
        favorites = request_body["favorites"]

        cur = conn.cursor()

        # start transaction
        conn.autocommit = False

        # find visitor by id
        sql = "SELECT * FROM visitors WHERE id = %s"
        cur.execute(sql, (id,))
        visitor = cur.fetchone()

        if not visitor:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Visitor not found"}),
            }

        # Actualizar el visitante en la tabla visitors usando el visitor_id
        update_visitor_query = """ UPDATE visitors SET favorites = %s WHERE id = %s """
        cur.execute(update_visitor_query, (favorites, id))

        conn.commit()
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Favorites updated successfully"}),
        }
    except Exception as e:
        if conn is not None:
            conn.rollback()
        return {"statusCode": 500, "body": json.dumps(str(e))}
    finally:
        if conn is not None:
            conn.close()
        if cur is not None:
            cur.close()