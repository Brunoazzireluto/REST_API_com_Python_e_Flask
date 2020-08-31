from flask_restful import Resource, reqparse
from models.hotel import Hotel_model
from flask_jwt_extended import jwt_required

class Hoteis(Resource):
    def get(self):
        return {"hoteis": [hotel.json() for hotel in Hotel_model.query.all()]} #SELECT * FROM hoteis

class Hotel(Resource):
    argumentos =reqparse.RequestParser()
    argumentos.add_argument("nome", type=str, required=True, help="The field 'nome' cannot be left in blank")
    argumentos.add_argument("estrelas")
    argumentos.add_argument("diaria", type=float, required=True, help="The field 'diaria' cannot be left in blank")
    argumentos.add_argument("cidade", type=str, required=True, help="The field 'cidade' cannot be left in blank")



    def get(self, hotel_id):
        hotel = Hotel_model.find_hotel(hotel_id)
        if hotel :
            return hotel.json()
                
        return{"message" : "Hotel not found"}, 404 #not found

    @jwt_required    
    def post(self, hotel_id):
        if Hotel_model.find_hotel(hotel_id):
            return {"message" : "Hotel id '{}' already exists.".format(hotel_id)}, 400 #badrequest

        dados = Hotel.argumentos.parse_args()
        hotel = Hotel_model(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return{"message": "An internal error ocurred trying to save hotel."}, 500 #Internal server error
        return hotel.json()

    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()               
        hotel_encontrado = Hotel_model.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados), 200 # sucess
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json()
        hotel = Hotel_model(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return{"message": "An internal error ocurred trying to save hotel."}, 500        
        return hotel.json(), 201 #Created
    @jwt_required
    def delete(self, hotel_id):
        hotel = Hotel_model.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return{"message": "An error ocurred trying to Delete hotel."}, 500
            return {"message" : "Hotel '{}' Deleted.".format(hotel_id)}
        return{"message": "Hotel '{}' not found.".format(hotel_id)}, 404