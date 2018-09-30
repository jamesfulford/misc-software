AIRPORT_ID1=$(curl -s -d "{\"airport\": \"AIRPORT1\"}" localhost:8000/airport)
AIRPORT_ID2=$(curl -s -d "{\"airport\": \"AIRPORT2\"}" localhost:8000/airport)
echo $AIRPORT_ID1 $(curl -s localhost:8000/airport/$AIRPORT_ID1)
echo $AIRPORT_ID2 $(curl -s localhost:8000/airport/$AIRPORT_ID2)
TRIP_ID1=$(curl -s -d "{\"from\": \"$AIRPORT_ID1\", \"to\": \"$AIRPORT_ID2\"}" localhost:8000/trip)
echo $TRIP_ID1 $(curl -s localhost:8000/trip/$TRIP_ID1)


TRIP_ID2=$(curl -s -d "{\"from\": \"$AIRPORT_ID1\", \"to\": \"$AIRPORT_ID1\"}" localhost:8000/trip)
echo $TRIP_ID2 $(curl -s localhost:8000/trip/$TRIP_ID2)

