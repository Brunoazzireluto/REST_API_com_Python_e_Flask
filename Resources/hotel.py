from flask_restful import Resource, reqparse
from models.hotel import Hotel_model
from flask_jwt_extended import jwt_required
from Resources.sites import SiteModel
import sqlite3
from Resources.filtros import normalize_path_params,consulta_com_cidade,consulta_sem_cidade


#path/hoteis?query=Rio de Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument("cidade", type=str)
path_params.add_argument("estrelas_min", type=float)
path_params.add_argument("estrelas_max", type=float)
path_params.add_argument("diaria_min", type=float)
path_params.add_argument("diaria_max", type=float)
path_params.add_argument("limit", type=float)
path_params.add_argument("offset", type=float)



class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect("banco.db")
        cursor = connection.cursor()
        
        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get("cidade"):
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_sem_cidade, tupla)

        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_com_cidade, tupla)
        hoteis = []
        for linha in resultado:
            hoteis.append({
            "hotel_id" : linha[0],
            "nome" : linha[1],
            "estrelas" : linha[2],
            "diaria" : linha[3],
            "cidade" : linha[4],
            "site_id" :linha[5]
            })

        return {"hoteis": hoteis}

class Hotel(Resource):
    argumentos =reqparse.RequestParser()
    argumentos.add_argument("nome", type=str, required=True, help="The field 'nome' cannot be left in blank")
    argumentos.add_argument("estrelas")
    argumentos.add_argument("diaria", type=float, required=True, help="The field 'diaria' cannot be left in blank")
    argumentos.add_argument("cidade", type=str, required=True, help="The field 'cidade' cannot be left in blank")
    argumentos.add_argument("site_id", type=int, required=True, help="The field 'site_id' cannot be left in blank")


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

        if not SiteModel.find_by_id(dados.get("site_id")):
            return {"message" : "The Hotel must be associated to a valid site id"}, 400
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