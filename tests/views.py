from flask import views

import blueprints as b


class ShowView(views.MethodView):

    def get(self):
        return 'show'


b.bp.add_url_rule(
    '/list', view_func=ShowView.as_view(b'list'),
    methods=['GET'])



