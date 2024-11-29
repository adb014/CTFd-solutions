from flask import Blueprint, redirect, render_template, request, url_for

from CTFd.models import Challenges, Solves, db
from CTFd.utils.config.pages import build_markdown
from CTFd.utils.decorators import admins_only
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers import markup
from CTFd.utils.logging import log
from CTFd.utils.user import is_admin, get_current_user

from .models import Solutions

plugin_bp = Blueprint('solutions', __name__, template_folder='templates', static_folder='static', static_url_path='/static/solutions')

def load_bp():

    @plugin_bp.route('/admin/solutions')
    @admins_only
    def solutions_list():
        q = request.args.get("q")
        field = request.args.get("field")
        filters = []

        if q:
            # The field exists as an exposed column
            if Challenges.__mapper__.has_property(field):
                filters.append(getattr(Challenges, field).like("%{}%".format(q)))

        query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())
        challenges = query.all()
        total = query.count()

        for challenge in challenges:
            solution = Solutions.query.filter_by(id=challenge.id).first()
            if solution:
                challenge.solution_state = solution.state
            else:
                challenge.solution_state = "hidden"

        return render_template(
            "list.html",
            challenges=challenges,
            total=total,
            q=q,
            field=field,
        )

    @plugin_bp.route('/admin/solutions/<int:challenge_id>')
    @admins_only
    def solutions_detail(challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        solution = Solutions.query.filter_by(id=challenge_id).first()
        if not solution:
            # There is no solution text for this change yet. Create it
            solution = Solutions(id=challenge_id, solution="", state = "hidden")
            db.session.add(solution)
            db.session.commit()
            db.session.flush()

        return render_template(
            "solution.html",
            challenge=challenge,
            challenge_html=markup(build_markdown(challenge.description)),
            solution=solution,
        )

    # Overload of /api/v1/challenges/<int:challenge_id>, treat solution
    # specific deletion and hand off the rest to the existing function
    @plugin_bp.route("/api/v1/solutions/<int:challenge_id>", methods = ['GET', 'DELETE', 'PATCH', 'POST'])
    @check_challenge_visibility
    def solutions_api(challenge_id):
        if request.method == 'GET':
            if is_admin():
                data = Solutions.query.filter(Solutions.id == challenge_id, Solutions.state != "hidden").first_or_404()
                if data:
                    solution_html = markup(build_markdown(data.solution))
                    return {"success": True, "data": {"id": data.id,
                                              "solution": data.solution,
                                              "solution_html": solution_html,
                                              "state": data.state}}
                else:
                    return {"success": False}
            else:
                user = get_current_user()
                if user:
                    solved = Solves.query.filter_by(challenge_id=challenge_id, user_id=user.id).first()
                    if solved:
                        visibility = "solved"
                    else:
                        visibility = "visible"
                else:
                    visibility = "visible"
                data = Solutions.query.filter_by(id=challenge_id).first()
                if data and (data.state == "visible" or data.state == visibility):
                    solution_html = markup(build_markdown(data.solution))
                    return {"success": True, "data": {"id": data.id,
                                              "solution": data.solution,
                                              "solution_html": solution_html,
                                              "state": data.state}}
                else:
                    return {"success": False}
        if not is_admin():
            return {"success": False, "errors": "Permission denied"}, 400

        if request.method == 'DELETE':
            data = Solutions.query.filter_by(id=challenge_id).first_or_404()
            if data:
                db.session.delete(data)
                db.session.commit()
                db.session.flush()
                return {"success": True}
            else:
                return {"success": False}, 404
        elif request.method == 'PATCH':
            data = Solutions.query.filter_by(id=challenge_id).first()
            req = request.get_json()
            if not data:
                return {"success": False, "errors": "Solution not found"}, 404
            if "solution" in req:
                data.solution = req["solution"]
            if "solution_state" in req:
                if req["solution_state"] == "visible":
                    data.state = "visible"
                elif req["solution_state"] == "solved":
                    data.state = "solved"
                elif req["solution_state"] == "admin":
                    data.state = "admin"
                else:
                    data.state = "hidden"
            else:
                data.data = "hidden"
            solution_html = markup(build_markdown(data.solution))
            db.session.commit()
            db.session.flush()
            return {"success": True, "data": {"id": data.id,
                                              "solution": data.solution,
                                              "solution_html": solution_html,
                                              "state": data.state}}
        elif request.method == 'POST':
            data = Solutions.query.filter_by(id=challenge_id).first()
            req = request.get_json()
            if data:
                # Create element, but allow overwriting of existing elements
                db.session.delete(data)
            solution = Solutions(id=challenge_id, solution="", visibility = False)
            if "solution" in req:
                data.solution = req["solution"]
            if "solution_state" in req:
                if req["solution_state"] == "visible":
                    data.state = "visible"
                elif req["solution_state"] == "solved":
                    data.state = "solved"
                elif req["solution_state"] == "admin":
                    data.state = "admin"
                else:
                    data.state = "hidden"
            else:
                data.data = "hidden"
            solution_html = markup(build_markdown(solution.solution))
            db.session.commit()
            db.session.flush()
            return {"success": True, "data": {"id": data.id,
                                              "solution": data.solution,
                                              "solution_html": solution_html,
                                              "state": data.state}}
        else:
            return {"success": False, "errors": "Permission denied"}, 400

    return plugin_bp








