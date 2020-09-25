from flask_restful import Resource, reqparse
from models.usuario import User_model
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST


atributos = reqparse.RequestParser()
atributos.add_argument("login", type=str, required=True, help="the field 'login' cannot be left in blank")
atributos.add_argument("senha", type=str, required=True, help="the field 'senha' cannot be left in blank")
atributos.add_argument("ativado", type=bool)

class User(Resource):
    #/usuarios/{user_id}
    def get(self, user_id):
        user = User_model.find_user (user_id)
        if user :
            return user.json()
                
        return{"message" : "User not found"}, 404 #not found

    @jwt_required 
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
        user.ativado = False
        user.save_user()
        return{"Message" : "User Created successfully!"}, 201

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = User_model.find_by_login(dados["login"])
        if user and safe_str_cmp(user.senha, dados["senha"]):
            if user.ativado:
                token_de_acesso = create_access_token(identity=user.user_id)
                return {"Access_token": token_de_acesso}, 200
            return{"Message" : "user not confirmed."},400    
        return {"Message" : "The username or password is incorrect"}, 401 #unathorize


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()["jti"] #JWT Token Identifier
        BLACKLIST.add(jwt_id)
        return {"Message": "Logged out successfully!"}, 200


class UserConfirm(Resource):
    #/confirmacao/{user_id}
    @classmethod
    def get(cls, user_id):
        user = User_model.find_user(user_id)

        if not user:
            return {"message": "User id '{}' not found.".format(user_id)}, 404
    
        user.ativado = True
        user.save_user()
        return{"Message":"User id '{}' confirme successfully.".format(user_id)},200