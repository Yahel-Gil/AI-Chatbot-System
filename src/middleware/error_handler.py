from flask import Flask, render_template
from http import HTTPStatus
from werkzeug.exceptions import HTTPException

def register_exception_handlers(server: Flask):

    @server.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found_handler(error: HTTPException):
        return render_template("pages/404.html"), HTTPStatus.NOT_FOUND

    @server.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_server_error_handler(error: Exception):
        return render_template("pages/404.html"), HTTPStatus.INTERNAL_SERVER_ERROR