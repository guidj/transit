def generate_graph(stops, routes, trips, fares, fare_rules, format='turtle'):

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

    for _, trip in trips.items():
        assert isinstance(trip, model.Trip)
        graph.add((URIRef(trip.uri), RDF.type, URIRef(trip.resource)))
        graph.add((URIRef(trip.uri), URIRef(schema_uri('headsign')), Literal(trip.headsign)))

        service = model.Service()
        service.id = trip.service_id
        route = model.Route()
        route.id = trip.route_id

        graph.add((URIRef(trip.uri), URIRef(schema_uri('service')), URIRef(service.uri)))
        graph.add((URIRef(route.uri), URIRef(schema_uri('trip')), URIRef(trip.uri)))

    for _, fare in fares.items():
        assert isinstance(fare, model.Fare)

        graph.add((URIRef(fare.uri), RDF.type, URIRef(fare.resource)))

        graph.add((URIRef(fare.transfer.uri), RDF.type, URIRef(fare.transfer.resource)))
        graph.add((URIRef(fare.transfer.uri), URIRef(schema_uri('transfers')), Literal(fare.transfer.transfers)))
        graph.add((URIRef(fare.transfer.uri), URIRef(schema_uri('transferDuration')),
                   Literal(fare.transfer.transfer_duration)))

        graph.add((URIRef(fare.pricing.uri), RDF.type, URIRef(fare.pricing.resource)))
        graph.add((URIRef(fare.pricing.uri), URIRef(schema_uri('price')), Literal(fare.pricing.price)))
        graph.add((URIRef(fare.pricing.uri), URIRef(schema_uri('currency')),
                   Literal(fare.pricing.currency)))
        graph.add((URIRef(fare.pricing.uri), URIRef(schema_uri('paymentMethod')),
                   Literal(fare.pricing.payment_method)))

        graph.add((URIRef(fare.transfer.uri), URIRef(schema_uri('fareTransfer')), URIRef(fare.transfer.uri)))
        graph.add((URIRef(fare.transfer.uri), URIRef(schema_uri('farePricing')), URIRef(fare.pricing.uri)))

    for _, fare_rule in fare_rules.items():

        assert isinstance(fare_rule, model.FareRule)

        fare = model.Fare()
        fare.id = fare_rule.fare_id
        graph.add((URIRef(fare_rule.uri), RDF.type, URIRef(fare_rule.resource)))
        graph.add((URIRef(fare_rule.uri), URIRef(schema_uri('fare')), URIRef(fare.uri)))

        if isinstance(fare_rule, model.RouteFareRule):
            route = model.Route()
            route.id = fare_rule.route_id
            graph.add((URIRef(fare_rule.uri), URIRef(schema_uri('route')), URIRef(route.uri)))

        elif isinstance(fare_rule, model.ZoneFareRule):
            zone = model.Zone()
            zone.id = fare_rule.zone_id
            graph.add((URIRef(fare_rule.uri), URIRef(schema_uri('zone')), URIRef(zone.uri)))

        elif isinstance(fare_rule, model.ZoneFareRule):
            origin, destination = model.Zone(), model.Zone()
            origin.id,destination.id = fare_rule.origin_id, fare_rule.destination_id

            graph.add((URIRef(fare_rule.uri), URIRef(schema_uri('originZone')), URIRef(origin.uri)))
            graph.add((URIRef(fare_rule.uri), URIRef(schema_uri('destinationZone')), URIRef(destination.uri)))

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
    trips = {}
    fares = {}
    fare_rules = {}

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

        # TODO: revise
        reader = csv.reader(StringIO.StringIO(zip_file.read('trips.txt')))

        # headers
        next(reader)

        for line in reader:

            trip = model.Trip()
            trip.id = line[2]
            trip.route_id = line[0]
            trip.service_id = line[1]
            trip.headsign = line[3]

            trips[trip.id] = trip

        reader = csv.reader(StringIO.StringIO(zip_file.read('fare_attributes.txt')))

        # headers
        next(reader)

        for line in reader:

            pricing = model.FarePricing()
            pricing.id = str(uuid.uuid4())
            pricing.price = line[1]
            pricing.currency = line[2]
            pricing.payment_method = 0
            transfer = model.FareTransfer()
            transfer.id = str(uuid.uuid4())
            transfer.transfers = line[4]
            transfer.transfer_duration = line[5]

            fare = model.Fare()
            fare.id = line[0]
            fare.pricing = pricing
            fare.transfer = transfer

            fares[fare.id] = fare

        reader = csv.reader(StringIO.StringIO(zip_file.read('fare_rules.txt')))

        # headers
        next(reader)

        for line in reader:

            fare_id, route_id, origin_id, destination_id, contains_id = line

            if not origin_id and not destination_id:

                # zone fare
                fare_rule = model.ZoneFareRule()
                fare_rule.fare_id = fare_id
                fare_rule.zone_id = contains_id

                fare_rules[fare_rule.id] = fare_rule

            if origin_id and destination_id:

                # zone cross fare
                fare_rule = model.ZoneCrossFareRule()
                fare_rule.id = str(uuid.uuid4())
                fare_rule.fare_id = fare_id
                fare_rule.origin_id = origin_id
                fare_rule.destination_id = destination_id

                fare_rules[fare_rule.id] = fare_rule

            if route_id:

                fare_rule = model.RouteFareRule()
                fare_rule.id = str(uuid.uuid4())
                fare_rule.route_id = route_id

                fare_rules[fare_rule.id] = fare_rule

    data = generate_graph(stops=stops, routes=routes, trips=trips, fares=fares,
                          fare_rules=fare_rules, format='xml')

    with open('data/transit-data.rdf', 'w') as fp:
        fp.write(data)
