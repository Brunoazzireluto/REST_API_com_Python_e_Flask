from flask_restful import Resource
from models.site import SiteModel


class Sites(Resource):
    def get(self):
        return{"sites" : [site.json() for site in SiteModel.query.all()]}

class Site(Resource):
    def get(self, url):
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {"Message": "site not found"}, 404

    def post(self, url):
        if SiteModel.find_site(url):
            return {"message" : "The site '{}' already exist".format(url)}, 400
        site = SiteModel(url)
        try:
            site.save_site()            
        except:
            return {"Message": "An internal error ocurred trying to create a new site"}
        return site.json()

    def delete(self,url):
        site = SiteModel.find_site(url)
        if site:
            site.delete.site()
            return{"Message": "Site Deleted"}
        return {"Message"  :"site not found"}, 404
