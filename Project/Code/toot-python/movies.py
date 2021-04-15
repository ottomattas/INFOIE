#!/usr/bin/env python
import os
from json import dumps
import logging

from flask import Flask, g, Response, request
from neo4j import GraphDatabase, basic_auth

app = Flask(__name__, static_url_path='/static/')

url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "abc")
neo4jVersion = os.getenv("NEO4J_VERSION", "")
database = os.getenv("NEO4J_DATABASE", "Movie Database")

#url = os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com")
#username = os.getenv("NEO4J_USER", "movies")
#password = os.getenv("NEO4J_PASSWORD", "movies")
#neo4jVersion = os.getenv("NEO4J_VERSION", "")
#database = os.getenv("NEO4J_DATABASE", "movies")

port = os.getenv("PORT", 8080)

driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
# This is our new query
@app.route("/icte")
def get_solution():
    db = get_db()
    q = "twister" #this is the query word /movie title
    results = db.read_transaction(lambda tx: list(tx.run('MATCH (:Environment { serverEnvironment: "Production"})<-[:IN_ENVIRONMENT]-(s:Server)-[:USED_BY]->(:Company { companyName: "Centralpoint"}), '
      '(sol:Solution { solutionId: "3"}) '
'RETURN sol '
                                                        )))
    return Response(dumps([serialize_movie(record['sol']) for record in results]),
                    mimetype="application/json")

def get_db():
    if not hasattr(g, 'neo4j_db'):
        if neo4jVersion.startswith("4"):
            g.neo4j_db = driver.session(database=database)
        else:
            g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


@app.route("/")
def get_index():
    return app.send_static_file('index.html')

def get_css():
    return app.send_static_file('style.css')

def get_js():
    return app.send_static_file('script.js')


def serialize_movie(sol):
    return {
        'id': sol['id'],
        'title': sol['solutionName']
    }


def serialize_cast(cast):
    return {
        'name': cast[0],
        'job': cast[1],
        'role': cast[2]
    }


@app.route("/graph")
def get_graph():
    db = get_db()
    #results = db.read_transaction(lambda tx: list(tx.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
    #                                                    "RETURN m.title as movie, collect(a.name) as cast "
     #                                                   "LIMIT $limit", {
     #                                                       "limit": request.args.get("limit",
     #                                                                                 100)})))

    #shows 3 company nodes and connected servers from the production environment
    #results = db.read_transaction(lambda tx: list(tx.run("MATCH (m:Company) <-[:USED_BY]-(s:Server)"
    #                                                    "RETURN m, m.title as Company, collect(s.serverName) as serverName "
    #                                                    "LIMIT $limit", {
    #                                                    "limit": request.args.get("limit",
    #                                                                                  100)})))

    # shows problem server, production environment and company. Solution as well but not connected
    results = db.read_transaction(lambda tx: list(tx.run('MATCH (n:Environment { serverEnvironment: "Production"})<-[:IN_ENVIRONMENT]-(s:Server{serverName:"clp-api-p01"})-[:USED_BY]->(c:Company { companyName:"Centralpoint"}), '
    '(sol:Solution { solutionId: "3"}) ' 
    'RETURN c.companyName as Company, sol.solutionName as Solution, collect(s.serverName) as serverName, collect(n.serverEnvironment) as serverEnv')))
    # n.serverEnvironment as serverEnv
                                                        #"LIMIT $limit", {
                                                        #"limit": request.args.get("limit",
                                                        #                              100)})))

    
                          

    #results = db.read_transaction(lambda tx: list(tx.run("MATCH (n) "
     #                                                    "RETURN n "
      #                                                    "LIMIT $limit", {
      #                                                        "limit": request.args.get("limit",
       #                                                                                 100)})))
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["Company"], "label": "Company"})
        target = i
        i += 1

        nodes.append({"title": record["Solution"], "label": "Solution"})
        target = i
        i += 1

        for serverName in record['serverName']:
            Server = {"title": serverName, "label": "Server"}
            try:
                source = nodes.index(Server)
            except ValueError:
                nodes.append(Server)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
            
            for serverEnv in record['serverEnv']:
                ServerE = {"title": serverEnv, "label": "serverEnvironment"}
                try:
                    source = nodes.index(ServerE)
                except ValueError:
                    nodes.append(ServerE)
                    source = i
                    i += 1
                rels.append({"source": source, "target": target})

        #for name in record['cast']:
        #    actor = {"title": name, "label": "actor"}
        #    try:
        #        source = nodes.index(actor)
        #    except ValueError:
        #        nodes.append(actor)
        #        source = i
        #        i += 1
        #    rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


@app.route("/graphAll")
def get_graphTwo():
    db = get_db()

    #shows 3 company nodes and connected servers from the production environment
    results = db.read_transaction(lambda tx: list(tx.run("MATCH (m:Company) <-[:USED_BY]-(s:Server)"
                                                        "RETURN m, m.title as Company, collect(s.serverName) as serverName "
                                                        "LIMIT $limit", {
                                                        "limit": request.args.get("limit",
                                                                                     100)})))
    
    nodes = []
    rels = []
    i = 0
    for record in results:
        nodes.append({"title": record["Company"], "label": "Company"})
        target = i
        i += 1

        for serverName in record['serverName']:
            Server = {"title": serverName, "label": "Server"}
            try:
                source = nodes.index(Server)
            except ValueError:
                nodes.append(Server)
                source = i
                i += 1
            rels.append({"source": source, "target": target})

        #for name in record['cast']:
        #    actor = {"title": name, "label": "actor"}
        #    try:
        #        source = nodes.index(actor)
        #    except ValueError:
        #        nodes.append(actor)
        #        source = i
        #        i += 1
        #    rels.append({"source": source, "target": target})
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")

@app.route("/search")
def get_search():
    try:
        q = request.args["q"]
    except KeyError:
        return []
    else:
        db = get_db()
        results = db.read_transaction(lambda tx: list(tx.run("MATCH (movie:Movie) "
                                                             "WHERE movie.title =~ $title "
                                                             "RETURN movie", {"title": "(?i).*" + q + ".*"}
                                                             )))
        return Response(dumps([serialize_movie(record['movie']) for record in results]),
                        mimetype="application/json")


@app.route("/movie/<title>")
def get_movie(title):
    db = get_db()
    result = db.read_transaction(lambda tx: tx.run("MATCH (movie:Movie {title:$title}) "
                                                   "OPTIONAL MATCH (movie)<-[r]-(person:Person) "
                                                   "RETURN movie.title as title,"
                                                   "COLLECT([person.name, "
                                                   "HEAD(SPLIT(TOLOWER(TYPE(r)), '_')), r.roles]) AS cast "
                                                   "LIMIT 1", {"title": title}).single())

    return Response(dumps({"title": result['title'],
                           "cast": [serialize_cast(member)
                                    for member in result['cast']]}),
                    mimetype="application/json")


if __name__ == '__main__':
    logging.info('Running on port %d, database is at %s', port, url)
    app.run(port=port)
