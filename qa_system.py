def run_query(query, session):
    result = session.run(query)
    return [record for record in result]

