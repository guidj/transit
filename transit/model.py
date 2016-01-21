BASE_URI = 'http://thinkingthread.com/ontologies/transit'


def schema_uri(entity):

    return '{0}#{1}'.format(BASE_URI, entity)


class Stop(object):

    id = None
    code = None
    name = None
    description = None
    location = None
    zone_id = None
    url = None
    parent_station_id = None

    @property
    def uri(self):
        return '{0}/resource/stops/{1}'.format(BASE_URI, self.id)

    @property
    def resource(self):
        return '{0}#{1}'.format(BASE_URI, self.__class__.__name__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Location(object):

    id = None
    latitude = None
    longitude = None

    @property
    def uri(self):
        return '{0}/resource/locations/{1}'.format(BASE_URI, self.id)

    @property
    def resource(self):
        return '{0}#{1}'.format(BASE_URI, self.__class__.__name__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Route(object):

    id = None
    agency_id = None
    short_name = None
    long_name = None
    description = None
    transport_type = None
    url = None
    # color = None
    # text_color = None

    @property
    def uri(self):
        return '{0}/resource/routes/{1}'.format(BASE_URI, self.id)

    @property
    def resource(self):
        return '{0}#{1}'.format(BASE_URI, self.__class__.__name__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class TransportType(object):

    @classmethod
    def transport(cls, id):

        uri = lambda x: '{0}#{1}'.format(BASE_URI, x)

        return {
            '0': uri('Tram'),
            '1': uri('Metro'),
            '2': uri('Rail'),
            '3': uri('Bus'),
            '4': uri('Ferry'),
            '5': uri('CableCar'),
            '6': uri('Gondola'),
            '7': uri('Funicular')
        }[id]


class Agency(object):

    id = None
    name = None
    url = None
    timezone = None
    language = None
    phone = None

    @property
    def uri(self):
        return '{0}/resource/agencies/{1}'.format(BASE_URI, self.id)

    @property
    def resource(self):
        return '{0}#{1}'.format(BASE_URI, self.__class__.__name__)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)
