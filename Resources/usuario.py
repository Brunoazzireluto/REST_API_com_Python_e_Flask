from flask_restful import Resource, reqparse
from models.usuario import User_model
from flask_jwt_extended import create_access_token
from werkzeug.security import safe_str_cmp


 atributos = reqparse.RequestParser()
        atributos.add_argument("login", type=str, required=True, help="the field 'login' cannot be left in blank")
        atributos.add_argument("senha", type=str, required=True, help="the field 'senha' cannot be left in blank")

class User(Resource):
    #/usuarios/{user_id}
    def get(self, user_id):
        user = User_model.find_user (user_id)
        if user :
            return user.json()
                
        return{"message" : "User not found"}, 404 #not found
        
    def delete(self, user_id):
        user = User_model.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return{"message": "An error ocurred trying to Delete hotel."}, 500
            return {"message" : "User  Deleted."}
        return{"message": "User  not found."}, 404


class User_register(Resource):
    #/cadastro
    def post(self):       
        dados = atributos.parse_args()

        if User_model.find_by_login(dados["login"]):
            return{"message" : "The login '{}' already exist." .format(dados["Login"])}

        user =  User_model(**dados)
        user.save_user()
        return{"Message" : "User Created successfully!"}, 201

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = User_model.find_by_login(dados["login"])
        if user and safe_str_cmp(user.senha, dados["senha"]):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {"Access_token": token_de_acesso}, 200
        return {"Message" : "The username or password is incorrect"}. 401 #unathorize