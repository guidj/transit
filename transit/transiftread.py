def generate_graph(stops, routes, format='turtle'):

    from rdflib import Graph, URIRef, Literal
    from rdflib import RDF
    from . import model
    from .model import schema_uri

    graph = Graph()
    # namespace = Namespace(model.BASE_URI)

    for _, stop in stops.items():
        assert isinstance(stop, model.Stop)
        graph.add((URIRef(stop.uri), RDF.type, URIRef(stop.resource)))
        graph.add((URIRef(stop.uri), URIRef(schema_uri('name')), Literal(stop.name)))
        graph.add((URIRef(stop.uri), URIRef(schema_uri('code')), Literal(stop.code)))
        graph.add((URIRef(stop.uri), URIRef(schema_uri('url')), Literal(stop.url)))

        if stop.location:
            assert isinstance(stop.location, model.Location)
            location = stop.location

            graph.add((URIRef(location.uri), RDF.type, URIRef(location.resource)))
            graph.add((URIRef(location.uri), URIRef(schema_uri('latitude')), Literal(float(location.latitude))))
            graph.add((URIRef(location.uri), URIRef(schema_uri('longitude')), Literal(float(location.longitude))))

            graph.add((URIRef(stop.uri), URIRef(schema_uri('location')), URIRef(location.uri)))

    for _, route in routes.items():
        assert isinstance(route, model.Route)
        graph.add((URIRef(route.uri), RDF.type, URIRef(route.resource)))
        graph.add((URIRef(route.agency_id), URIRef(schema_uri('operates')), URIRef(route.uri)))
        graph.add((URIRef(route.uri), URIRef(schema_uri('shortName')), Literal(route.short_name)))
        graph.add((URIRef(route.uri), URIRef(schema_uri('longName')), Literal(route.long_name)))
        graph.add((URIRef(route.uri), URIRef(schema_uri('url')), Literal(route.url)))
        graph.add((URIRef(route.uri), URIRef(schema_uri('transportType')), URIRef(route.transport_type)))

    return graph.serialize(format=format)


if __name__ == '__main__':

    import sys
    import csv
    import zipfile
    import StringIO
    import uuid

    from . import model

    inp = sys.argv[1]

    # TODO: validate file
    # feed = transitfeed.Loader(inp)
    # schedule = feed.Load()
    #
    # stops = schedule.GetStopList()

    stops = {}
    agencies = {}
    routes = {}

    with open(inp, 'rb') as zfp:
        zip_file = zipfile.ZipFile(zfp)

        # TODO: revise
        reader = csv.reader(StringIO.StringIO(zip_file.read('stops.txt')))

        # headers
        next(reader)

        for line in reader:

            stop = model.Stop()
            stop.id = line[0]
            stop.code = line[1]
            stop.name = line[2]
            stop.url = line[6]
            if line[3] and line[4]:
                location = model.Location()
                location.id = str(uuid.uuid4())
                location.latitude = line[3]
                location.longitude = line[4]
                stop.location = location

            stops[stop.id] = stop

        # TODO: revise
        reader = csv.reader(StringIO.StringIO(zip_file.read('routes.txt')))

        # headers
        next(reader)

        for line in reader:

            route = model.Route()
            route.id = line[0]
            route.agency_id = line[1]
            route.short_name = line[2]
            route.long_name = line[3]
            route.description = line[4]
            route.transport_type = model.TransportType.transport(line[5])
            route.url = line[6]
            # route.color = line[7]
            # route.text_color = line[8]

            routes[route.id] = route

    data = generate_graph(stops=stops, routes=routes)

    with open('data/transit-data.rdf', 'w') as fp:
        fp.write(data)
