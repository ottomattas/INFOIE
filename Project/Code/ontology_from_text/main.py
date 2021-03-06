import matplotlib.pyplot as plt
import networkx as nx
import spacy
from spacy.lang.en import English


def getSentences(text):
    nlp = English()
    nlp.add_pipe(nlp.create_pipe('sentencizer'))
    # nlp.add_pipe(nlp.create_pipe('parser'))
    document = nlp(text)
    return [sent.string.strip() for sent in document.sents]


def printToken(token):
    print(token.text, "->", token.dep_)


def appendChunk(original, chunk):
    return original + ' ' + chunk


def isRelationCandidate(token):
    deps = ["ROOT", "adj", "attr", "agent", "amod"]
    return any(subs in token.dep_ for subs in deps)


def isConstructionCandidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)


def processSubjectObjectPairs(tokens):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        printToken(token)
        if "punct" in token.dep_:
            continue
        if isRelationCandidate(token):
            relation = appendChunk(relation, token.lemma_)
        if isConstructionCandidate(token):
            if subjectConstruction:
                subjectConstruction = appendChunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = appendChunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = appendChunk(subject, token.text)
            subject = appendChunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = appendChunk(object, token.text)
            object = appendChunk(objectConstruction, object)
            objectConstruction = ''

    print(subject.strip(), ",", relation.strip(), ",", object.strip())
    return (subject.strip(), relation.strip(), object.strip())


def processSentence(sentence):
    tokens = nlp_model(sentence)
    return processSubjectObjectPairs(tokens)


def printGraph(triples):
    G = nx.Graph()
    for triple in triples:
        G.add_node(triple[0])
        G.add_node(triple[1])
        G.add_node(triple[2])
        G.add_edge(triple[0], triple[1])
        G.add_edge(triple[1], triple[2])

    pos = nx.spring_layout(G, k=0.5, iterations=100)
    plt.figure(figsize=(15, 10))
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
            node_size=500, node_color='seagreen', alpha=0.9,
            labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.show()


if __name__ == "__main__":

    # text = "London is the capital and largest city of England and the United Kingdom. Standing on the River " \
    #        "Thames in the south-east of England, at the head of its 50-mile (80 km) estuary leading to " \
    #        "the North Sea, London has been a major settlement for two millennia. " \
    #        "Londinium was founded by the Romans. The City of London, " \
    #        "London's ancient core − an area of just 1.12 square miles (2.9 km2) and colloquially known as " \
    #        "the Square Mile − retains boundaries that follow closely its medieval limits." \
    #        "The City of Westminster is also an Inner London borough holding city status. " \
    #        "Greater London is governed by the Mayor of London and the London Assembly." \
    #        "London is located in the southeast of England." \
    #        "Westminster is located in London." \
    #        "London is the biggest city in Britain. London has a population of 7,172,036."

    # text = '''A server is a piece of computer hardware or software (computer program) that provides
    # functionality for other programs or devices, called "clients". This architecture is called the client–server model.
    # Servers can provide various functionalities, often called "services", such as sharing data or resources among multiple clients,
    # or performing computation for a client. A single server can serve multiple clients, and a single client can use multiple servers.
    # A client process may run on the same device or may connect over a network to a server on a different device.
    # Typical servers are database servers, file servers, mail servers, print servers, web servers, game servers, and application servers.
    # Client–server systems are today most frequently implemented by (and often identified with) the request–response model:
    # a client sends a request to the server, which performs some action and sends a response back to the client,
    # typically with a result or acknowledgment. Designating a computer as "server-class hardware" implies that it is specialized
    # for running servers on it. This often implies that it is more powerful and reliable than standard personal computers,
    # but alternatively, large computing clusters may be composed of many relatively simple, replaceable server components.'''

    text = '''A server provides data to machines. 
              A server serves data.
              A server works over the internet.
              A server provides functionality. 
              A server serves multiple clients.
              A server performs some action.
              A server sends responses to client.
              A client can use multiple servers. 
              A client connects to a server.
              A client sends a request to the server.
              '''

    sentences = getSentences(text)
    nlp_model = spacy.load('en_core_web_sm')

    triples = []
    print(text)
    for sentence in sentences:
        triples.append(processSentence(sentence))

    printGraph(triples)
