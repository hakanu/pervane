# """THIS FILE IS UNUSED, main contents is in init.py
# """
# from flask import render_template
# from flask_appbuilder.models.sqla.interface import SQLAInterface
# from flask_appbuilder import ModelView, ModelRestApi
# from flask_appbuilder.baseviews import BaseView, expose

# from . import appbuilder, db

# print('app args: ', app_args)
# """
#     Create your Model based REST API::

#     class MyModelApi(ModelRestApi):
#         datamodel = SQLAInterface(MyModel)

#     appbuilder.add_api(MyModelApi)


#     Create your Views::


#     class MyModelView(ModelView):
#         datamodel = SQLAInterface(MyModel)


#     Next, register your Views::


#     appbuilder.add_view(
#         MyModelView,
#         "My View",
#         icon="fa-folder-open-o",
#         category="My Category",
#         category_icon='fa-envelope'
#     )
# """

# """
#     Application wide 404 error handler
# """
# class MyView(BaseView):
#   route_base = "/myview"

#   @expose('/method1/<string:param1>')
#   def method1(self, param1):
#     # do something with param1
#     # and return it
#     return param1

#   @expose('/method2/<string:param1>')
#   def method2(self, param1):
#     """http://localhost:8081/myview/method2/asdas"""
#     # do something with param1
#     # and render it
#     param1 = 'Hello %s' % (param1)
#     return param1


# appbuilder.add_view_no_menu(MyView())


# @appbuilder.app.errorhandler(404)
# def page_not_found(e):
#   return (
#       render_template(
#           "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
#       ),
#       404,
#   )


# db.create_all()
