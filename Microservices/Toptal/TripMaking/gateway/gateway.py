import json

from nameko.rpc import RpcProxy
from nameko.web.handlers import http


class GatewayService:
    name = 'gateway'

    airports_rpc = RpcProxy('airports_service')
    trips_rpc = RpcProxy('trips_service')

    @http('GET', '/airport/<string:airport_id>')
    def get_airport(self, request, airport_id):
        airport = self.airports_rpc.get(airport_id)
        return json.dumps({'airport': airport})

    @http('POST', '/airport')
    def post_airport(self, request):
        data = json.loads(request.get_data(as_text=True))
        airport_id = self.airports_rpc.create(data['airport'])

        return airport_id

    @http('GET', '/trip/<string:trip_id>')
    def get_trip(self, request, trip_id):
        trip = self.trips_rpc.get(trip_id)
        return json.dumps({'trip': trip})

    @http('POST', '/trip')
    def post_trip(self, request):
        """
        request = {
            "from": "{{ airport.id1 }}",
            "to": "{{ airport.id2 }}"
        }
        Where airport.id1 != airport.id2
        """
        data = json.loads(request.get_data(as_text=True))
        assert data["from"] != data["to"]
        trip_id = self.trips_rpc.create(data['from'], data['to'])

        return trip_id
